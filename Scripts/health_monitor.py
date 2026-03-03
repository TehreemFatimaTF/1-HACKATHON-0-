#!/usr/bin/env python3
"""
Health Monitor & Watchdog
Monitors all system processes and sends alerts on failures
"""

import os
import sys
import time
import json
import psutil
import subprocess
from datetime import datetime
from pathlib import Path

# Configuration
BASE_DIR = Path(__file__).parent.parent
LOGS_DIR = BASE_DIR / "Logs"
HEALTH_LOG = LOGS_DIR / "health_monitor.log"
HEALTH_STATUS = LOGS_DIR / "health_status.json"

# Check interval (seconds)
CHECK_INTERVAL = 60  # Check every minute

# Alert thresholds
MAX_MEMORY_MB = 1024  # 1GB
MAX_CPU_PERCENT = 80
MAX_RESTART_COUNT = 5

# Processes to monitor
MONITORED_PROCESSES = [
    {
        "name": "gmail-watcher",
        "script": "watcher_gmail.py",
        "critical": True
    },
    {
        "name": "whatsapp-watcher",
        "script": "watcher_whatsapp.py",
        "critical": True
    },
    {
        "name": "orchestrator",
        "script": "orchestrator.py",
        "critical": True
    }
]


class HealthMonitor:
    """Monitors system health and sends alerts"""

    def __init__(self):
        self.running = False
        self.health_data = self.load_health_data()

        # Ensure logs directory exists
        LOGS_DIR.mkdir(exist_ok=True)

    def log(self, message, level="INFO"):
        """Log messages to file and console"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [HEALTH] [{level}] {message}"
        print(log_entry)

        with open(HEALTH_LOG, 'a', encoding='utf-8') as f:
            f.write(log_entry + "\n")

    def load_health_data(self):
        """Load health data from file"""
        default_data = {
            "last_check": None,
            "total_checks": 0,
            "alerts_sent": 0,
            "processes": {}
        }

        if HEALTH_STATUS.exists():
            try:
                with open(HEALTH_STATUS, 'r') as f:
                    loaded = json.load(f)
                    default_data.update(loaded)
                    return default_data
            except Exception as e:
                self.log(f"Error loading health data: {e}", "WARNING")

        return default_data

    def save_health_data(self):
        """Save health data to file"""
        try:
            self.health_data['last_check'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(HEALTH_STATUS, 'w') as f:
                json.dump(self.health_data, f, indent=2)
        except Exception as e:
            self.log(f"Error saving health data: {e}", "ERROR")

    def find_process_by_script(self, script_name):
        """Find process by script name"""
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'status']):
            try:
                cmdline = proc.info.get('cmdline', [])
                if cmdline and any(script_name in arg for arg in cmdline):
                    return proc
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return None

    def check_process_health(self, process_info):
        """Check health of a single process"""
        script_name = process_info['script']
        process_name = process_info['name']
        is_critical = process_info['critical']

        # Initialize process data if not exists
        if process_name not in self.health_data['processes']:
            self.health_data['processes'][process_name] = {
                "status": "unknown",
                "last_seen": None,
                "restart_count": 0,
                "last_alert": None
            }

        proc_data = self.health_data['processes'][process_name]

        # Find the process
        proc = self.find_process_by_script(script_name)

        if proc is None:
            # Process not running
            if proc_data['status'] != 'down':
                self.log(f"[ALERT] Process '{process_name}' is DOWN!", "ERROR")
                self.send_alert(
                    f"Process Down: {process_name}",
                    f"Critical process '{process_name}' ({script_name}) is not running!"
                )
                proc_data['status'] = 'down'
                proc_data['restart_count'] += 1

            return {
                "name": process_name,
                "status": "down",
                "critical": is_critical
            }

        # Process is running - check health metrics
        try:
            cpu_percent = proc.cpu_percent(interval=0.1)
            memory_info = proc.memory_info()
            memory_mb = memory_info.rss / (1024 * 1024)
            status = proc.status()

            # Update process data
            proc_data['status'] = 'running'
            proc_data['last_seen'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Check for issues
            issues = []

            if memory_mb > MAX_MEMORY_MB:
                issues.append(f"High memory: {memory_mb:.1f}MB")
                self.log(f"[WARNING] {process_name} using {memory_mb:.1f}MB memory", "WARNING")

            if cpu_percent > MAX_CPU_PERCENT:
                issues.append(f"High CPU: {cpu_percent:.1f}%")
                self.log(f"[WARNING] {process_name} using {cpu_percent:.1f}% CPU", "WARNING")

            if status == 'zombie':
                issues.append("Process is zombie")
                self.log(f"[ERROR] {process_name} is a zombie process!", "ERROR")

            if proc_data['restart_count'] > MAX_RESTART_COUNT:
                issues.append(f"Too many restarts: {proc_data['restart_count']}")
                self.log(f"[ERROR] {process_name} has restarted {proc_data['restart_count']} times", "ERROR")

            # Send alert if there are issues
            if issues and is_critical:
                self.send_alert(
                    f"Process Issues: {process_name}",
                    f"Process '{process_name}' has issues:\n" + "\n".join(f"- {issue}" for issue in issues)
                )

            return {
                "name": process_name,
                "status": "running",
                "pid": proc.pid,
                "cpu_percent": cpu_percent,
                "memory_mb": memory_mb,
                "issues": issues,
                "critical": is_critical
            }

        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            self.log(f"Error checking {process_name}: {e}", "ERROR")
            return {
                "name": process_name,
                "status": "error",
                "critical": is_critical
            }

    def check_disk_space(self):
        """Check available disk space"""
        try:
            disk = psutil.disk_usage(str(BASE_DIR))
            free_gb = disk.free / (1024 ** 3)
            percent_used = disk.percent

            if percent_used > 90:
                self.log(f"[ALERT] Disk space critical: {percent_used}% used", "ERROR")
                self.send_alert(
                    "Disk Space Critical",
                    f"Disk usage at {percent_used}% - only {free_gb:.1f}GB free"
                )
            elif percent_used > 80:
                self.log(f"[WARNING] Disk space low: {percent_used}% used", "WARNING")

            return {
                "free_gb": free_gb,
                "percent_used": percent_used
            }
        except Exception as e:
            self.log(f"Error checking disk space: {e}", "ERROR")
            return None

    def check_log_files(self):
        """Check if log files are growing (indicates activity)"""
        log_files = [
            LOGS_DIR / "watcher_gmail.log",
            LOGS_DIR / "watcher_whatsapp.log",
            LOGS_DIR / "orchestrator.log"
        ]

        stale_logs = []
        for log_file in log_files:
            if log_file.exists():
                mtime = log_file.stat().st_mtime
                age_hours = (time.time() - mtime) / 3600

                if age_hours > 2:  # No activity in 2 hours
                    stale_logs.append(f"{log_file.name} ({age_hours:.1f}h old)")

        if stale_logs:
            self.log(f"[WARNING] Stale log files detected: {', '.join(stale_logs)}", "WARNING")

        return stale_logs

    def send_alert(self, subject, message):
        """Send alert (log for now, can integrate with email/Slack MCP)"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        alert_file = LOGS_DIR / "alerts.log"
        with open(alert_file, 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"[{timestamp}] ALERT: {subject}\n")
            f.write(f"{'='*60}\n")
            f.write(f"{message}\n")
            f.write(f"{'='*60}\n\n")

        self.health_data['alerts_sent'] += 1

        # Try to send email alert via MCP (if configured)
        self.try_send_email_alert(subject, message)

        # Try to send Slack alert via MCP (if configured)
        self.try_send_slack_alert(subject, message)

    def try_send_email_alert(self, subject, message):
        """Try to send email alert via MCP"""
        try:
            # Check if MCP email queue exists
            mcp_queue = BASE_DIR / "Logs" / "mcp_email_queue.json"
            if not mcp_queue.exists():
                return

            # Load existing queue
            with open(mcp_queue, 'r') as f:
                queue = json.load(f)

            # Add alert to queue
            alert_email = {
                "to": "admin@example.com",  # Configure this
                "subject": f"[ALERT] {subject}",
                "body": f"""
System Alert from AI Employee Health Monitor

Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Alert: {subject}

Details:
{message}

---
This is an automated alert from the AI Employee health monitoring system.
""",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "priority": "high",
                "type": "alert"
            }

            queue.append(alert_email)

            # Save queue
            with open(mcp_queue, 'w') as f:
                json.dump(queue, f, indent=2)

            self.log("Alert queued for email delivery", "INFO")

        except Exception as e:
            self.log(f"Failed to queue email alert: {e}", "WARNING")

    def try_send_slack_alert(self, subject, message):
        """Try to send Slack alert via webhook"""
        try:
            # Check if Slack webhook is configured
            slack_config = BASE_DIR / "slack_webhook.json"
            if not slack_config.exists():
                return

            with open(slack_config, 'r') as f:
                config = json.load(f)
                webhook_url = config.get('webhook_url')

            if not webhook_url:
                return

            # Prepare Slack message
            slack_message = {
                "text": f"🚨 *{subject}*",
                "blocks": [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": f"🚨 {subject}"
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": message
                        }
                    },
                    {
                        "type": "context",
                        "elements": [
                            {
                                "type": "mrkdwn",
                                "text": f"*Time:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                            }
                        ]
                    }
                ]
            }

            # Send to Slack (requires requests library)
            import requests
            response = requests.post(webhook_url, json=slack_message, timeout=5)

            if response.status_code == 200:
                self.log("Alert sent to Slack", "INFO")
            else:
                self.log(f"Slack alert failed: {response.status_code}", "WARNING")

        except ImportError:
            # requests library not available
            pass
        except Exception as e:
            self.log(f"Failed to send Slack alert: {e}", "WARNING")

    def run_health_check(self):
        """Run complete health check"""
        self.log("=" * 60, "SYSTEM")
        self.log("Running health check...", "SYSTEM")
        self.log("=" * 60, "SYSTEM")

        results = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "processes": [],
            "disk": None,
            "stale_logs": []
        }

        # Check all monitored processes
        for process_info in MONITORED_PROCESSES:
            health = self.check_process_health(process_info)
            results['processes'].append(health)

            status_icon = "✓" if health['status'] == 'running' else "✗"
            self.log(f"{status_icon} {health['name']}: {health['status']}", "INFO")

        # Check disk space
        disk_info = self.check_disk_space()
        if disk_info:
            results['disk'] = disk_info
            self.log(f"Disk: {disk_info['free_gb']:.1f}GB free ({disk_info['percent_used']}% used)", "INFO")

        # Check log files
        stale_logs = self.check_log_files()
        results['stale_logs'] = stale_logs

        # Update counters
        self.health_data['total_checks'] += 1
        self.save_health_data()

        self.log("=" * 60, "SYSTEM")
        self.log(f"Health check complete (Total: {self.health_data['total_checks']})", "SUCCESS")
        self.log("=" * 60, "SYSTEM")

        return results

    def start(self):
        """Start health monitoring loop"""
        self.running = True
        self.log("=" * 60, "SYSTEM")
        self.log("=== Health Monitor Starting ===", "SYSTEM")
        self.log("=" * 60, "SYSTEM")
        self.log(f"Check interval: {CHECK_INTERVAL} seconds")
        self.log(f"Monitoring {len(MONITORED_PROCESSES)} processes")

        try:
            while self.running:
                self.run_health_check()
                time.sleep(CHECK_INTERVAL)

        except KeyboardInterrupt:
            self.stop()
        except Exception as e:
            self.log(f"Unexpected error: {e}", "ERROR")
            self.stop()

    def stop(self):
        """Stop health monitoring"""
        self.log("=" * 60, "SYSTEM")
        self.log("=== Shutting down health monitor ===", "SYSTEM")
        self.running = False
        self.save_health_data()
        self.log("Health monitor stopped")
        self.log("=" * 60, "SYSTEM")


if __name__ == "__main__":
    monitor = HealthMonitor()
    monitor.start()
