"""
Performance Monitoring Utility for Gold Tier Autonomous Employee

Tracks processing time, memory usage, and system metrics for autonomous operations.
Part of T100 - Performance monitoring implementation.

Usage:
    from src.utils.performance_monitor import PerformanceMonitor

    monitor = PerformanceMonitor()

    with monitor.track("task_processing"):
        # Your code here
        pass

    metrics = monitor.get_metrics()
"""

import time
import psutil
import json
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path
from contextlib import contextmanager


class PerformanceMonitor:
    """
    Tracks performance metrics for autonomous operations

    Features:
    - Processing time tracking
    - Memory usage monitoring
    - CPU usage tracking
    - Metrics persistence to JSON
    - Real-time alerts for performance degradation
    """

    def __init__(self, metrics_file: Optional[Path] = None):
        """
        Initialize performance monitor

        Args:
            metrics_file: Path to metrics storage file (default: Logs/performance_metrics.json)
        """
        if metrics_file is None:
            metrics_file = Path("Logs/performance_metrics.json")

        self.metrics_file = metrics_file
        self.current_metrics: Dict[str, Any] = {}
        self.process = psutil.Process()

        # Performance thresholds
        self.thresholds = {
            "max_processing_time_seconds": 300,  # 5 minutes
            "max_memory_mb": 1024,  # 1 GB
            "max_cpu_percent": 80,
        }

    @contextmanager
    def track(self, operation_name: str):
        """
        Context manager to track operation performance

        Args:
            operation_name: Name of the operation being tracked

        Usage:
            with monitor.track("invoice_creation"):
                create_invoice()
        """
        start_time = time.time()
        start_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        start_cpu = self.process.cpu_percent()

        try:
            yield

            # Calculate metrics
            end_time = time.time()
            end_memory = self.process.memory_info().rss / 1024 / 1024  # MB
            end_cpu = self.process.cpu_percent()

            duration = end_time - start_time
            memory_delta = end_memory - start_memory

            # Store metrics
            metric_entry = {
                "operation": operation_name,
                "timestamp": datetime.now().isoformat(),
                "duration_seconds": round(duration, 3),
                "memory_start_mb": round(start_memory, 2),
                "memory_end_mb": round(end_memory, 2),
                "memory_delta_mb": round(memory_delta, 2),
                "cpu_percent": round(end_cpu, 2),
                "status": "success"
            }

            # Check thresholds
            alerts = []
            if duration > self.thresholds["max_processing_time_seconds"]:
                alerts.append(f"Processing time exceeded threshold: {duration:.2f}s")

            if end_memory > self.thresholds["max_memory_mb"]:
                alerts.append(f"Memory usage exceeded threshold: {end_memory:.2f}MB")

            if end_cpu > self.thresholds["max_cpu_percent"]:
                alerts.append(f"CPU usage exceeded threshold: {end_cpu:.2f}%")

            if alerts:
                metric_entry["alerts"] = alerts

            self._save_metric(metric_entry)

        except Exception as e:
            # Track failed operations
            end_time = time.time()
            duration = end_time - start_time

            metric_entry = {
                "operation": operation_name,
                "timestamp": datetime.now().isoformat(),
                "duration_seconds": round(duration, 3),
                "status": "failed",
                "error": str(e)
            }

            self._save_metric(metric_entry)
            raise

    def _save_metric(self, metric: Dict[str, Any]):
        """Save metric to file"""
        try:
            # Load existing metrics
            if self.metrics_file.exists():
                with open(self.metrics_file, 'r') as f:
                    metrics = json.load(f)
            else:
                metrics = {"metrics": []}

            # Append new metric
            metrics["metrics"].append(metric)

            # Keep only last 1000 metrics to prevent file bloat
            if len(metrics["metrics"]) > 1000:
                metrics["metrics"] = metrics["metrics"][-1000:]

            # Save back
            self.metrics_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.metrics_file, 'w') as f:
                json.dump(metrics, f, indent=2)

        except Exception as e:
            print(f"Warning: Failed to save performance metric: {e}")

    def get_metrics(self, operation_name: Optional[str] = None,
                   limit: int = 100) -> Dict[str, Any]:
        """
        Retrieve performance metrics

        Args:
            operation_name: Filter by operation name (optional)
            limit: Maximum number of metrics to return

        Returns:
            Dictionary with metrics and summary statistics
        """
        if not self.metrics_file.exists():
            return {"metrics": [], "summary": {}}

        with open(self.metrics_file, 'r') as f:
            data = json.load(f)

        metrics = data.get("metrics", [])

        # Filter by operation name if specified
        if operation_name:
            metrics = [m for m in metrics if m.get("operation") == operation_name]

        # Limit results
        metrics = metrics[-limit:]

        # Calculate summary statistics
        if metrics:
            durations = [m["duration_seconds"] for m in metrics if "duration_seconds" in m]
            memory_deltas = [m["memory_delta_mb"] for m in metrics if "memory_delta_mb" in m]

            summary = {
                "total_operations": len(metrics),
                "successful_operations": len([m for m in metrics if m.get("status") == "success"]),
                "failed_operations": len([m for m in metrics if m.get("status") == "failed"]),
                "avg_duration_seconds": round(sum(durations) / len(durations), 3) if durations else 0,
                "max_duration_seconds": round(max(durations), 3) if durations else 0,
                "avg_memory_delta_mb": round(sum(memory_deltas) / len(memory_deltas), 2) if memory_deltas else 0,
                "alerts_count": len([m for m in metrics if "alerts" in m])
            }
        else:
            summary = {}

        return {
            "metrics": metrics,
            "summary": summary
        }

    def get_system_status(self) -> Dict[str, Any]:
        """
        Get current system resource usage

        Returns:
            Dictionary with current CPU, memory, and disk usage
        """
        return {
            "timestamp": datetime.now().isoformat(),
            "cpu_percent": round(psutil.cpu_percent(interval=1), 2),
            "memory_percent": round(psutil.virtual_memory().percent, 2),
            "memory_available_mb": round(psutil.virtual_memory().available / 1024 / 1024, 2),
            "disk_percent": round(psutil.disk_usage('/').percent, 2),
            "process_memory_mb": round(self.process.memory_info().rss / 1024 / 1024, 2),
            "process_cpu_percent": round(self.process.cpu_percent(), 2)
        }


# Global instance for easy access
_global_monitor = None


def get_monitor() -> PerformanceMonitor:
    """Get global performance monitor instance"""
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = PerformanceMonitor()
    return _global_monitor
