"""
Generate Weekly Audit Report for CEO Briefing

This script reads Action_Logs.json and generates a Jeff Bezos-style narrative report
in Management/CEO_WEEKLY_BRIEFING.md with success rate analysis.

Usage:
    python generate_weekly_audit.py
    python generate_weekly_audit.py --test  # Test mode with sample data
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict


def load_action_logs(logs_path="Logs/Action_Logs.json"):
    """Load action logs from JSON file."""
    try:
        with open(logs_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: {logs_path} not found")
        return []
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {logs_path}")
        return []


def calculate_metrics(logs):
    """Calculate success rates and metrics from action logs."""
    total_actions = len(logs)
    if total_actions == 0:
        return {
            'total': 0,
            'success_count': 0,
            'failure_count': 0,
            'success_rate': 0,
            'by_type': {},
            'recent_failures': []
        }
    
    success_count = sum(1 for log in logs if log.get('status') == 'SUCCESS')
    failure_count = sum(1 for log in logs if log.get('status') == 'FAILURE')
    success_rate = (success_count / total_actions) * 100 if total_actions > 0 else 0
    
    # Group by action type
    by_type = defaultdict(lambda: {'total': 0, 'success': 0, 'failure': 0})
    for log in logs:
        action_type = log.get('action_type', 'UNKNOWN')
        status = log.get('status', 'UNKNOWN')
        by_type[action_type]['total'] += 1
        if status == 'SUCCESS':
            by_type[action_type]['success'] += 1
        elif status == 'FAILURE':
            by_type[action_type]['failure'] += 1
    
    # Get recent failures
    recent_failures = [
        log for log in logs 
        if log.get('status') == 'FAILURE'
    ][-5:]  # Last 5 failures
    
    return {
        'total': total_actions,
        'success_count': success_count,
        'failure_count': failure_count,
        'success_rate': success_rate,
        'by_type': dict(by_type),
        'recent_failures': recent_failures
    }


def generate_bezos_narrative(metrics):
    """Generate Jeff Bezos-style narrative report."""
    narrative = f"""# CEO Weekly Briefing
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## Executive Summary

This week, our Digital FTE processed **{metrics['total']} actions** with a **{metrics['success_rate']:.1f}% success rate**. 

"""
    
    # Success/Failure analysis
    if metrics['success_rate'] >= 95:
        narrative += """**Performance Assessment:** Excellent. The system is operating at peak efficiency.

"""
    elif metrics['success_rate'] >= 85:
        narrative += """**Performance Assessment:** Good. Minor optimization opportunities exist.

"""
    elif metrics['success_rate'] >= 70:
        narrative += """**Performance Assessment:** Acceptable. Attention required to improve reliability.

"""
    else:
        narrative += """**Performance Assessment:** Below expectations. Immediate intervention required.

"""
    
    # Breakdown by action type
    narrative += """## Action Breakdown

| Action Type | Total | Success | Failure | Success Rate |
|-------------|-------|---------|---------|--------------|
"""
    
    for action_type, stats in metrics['by_type'].items():
        rate = (stats['success'] / stats['total'] * 100) if stats['total'] > 0 else 0
        narrative += f"| {action_type} | {stats['total']} | {stats['success']} | {stats['failure']} | {rate:.1f}% |\n"
    
    # Recent failures
    if metrics['recent_failures']:
        narrative += f"""
## Recent Failures ({len(metrics['recent_failures'])})

The following actions require attention:

"""
        for i, failure in enumerate(metrics['recent_failures'], 1):
            timestamp = failure.get('timestamp', 'Unknown')
            action_type = failure.get('action_type', 'Unknown')
            file_name = failure.get('file', 'Unknown')
            error = failure.get('error', 'No error message')
            
            narrative += f"""### {i}. {action_type} - {timestamp}
- **File:** `{file_name}`
- **Error:** {error}

"""
    else:
        narrative += """
## Recent Failures

No failures recorded. All systems operating nominally.

"""
    
    # Recommendations
    narrative += """## Recommendations

"""
    
    if metrics['success_rate'] < 85:
        narrative += """1. **Immediate Action Required:** Review failure patterns and implement corrective measures
2. **Process Improvement:** Enhance validation and error handling mechanisms
3. **Monitoring:** Increase monitoring frequency for critical action types

"""
    elif metrics['failure_count'] > 0:
        narrative += """1. **Continuous Improvement:** Analyze failure cases for optimization opportunities
2. **Preventive Measures:** Implement additional safeguards for identified failure patterns

"""
    else:
        narrative += """1. **Maintain Excellence:** Continue current operational procedures
2. **Scale Readiness:** System is ready for increased workload

"""
    
    narrative += """---

*This report is generated automatically by the Chief of Staff skill.*
*For detailed logs, see `Logs/Action_Logs.json`*
"""
    
    return narrative


def save_briefing(narrative, output_path="Management/CEO_WEEKLY_BRIEFING.md"):
    """Save the briefing to markdown file."""
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(narrative)
    
    print(f"✓ CEO Briefing saved to: {output_path}")


def main():
    """Main execution function."""
    # Check for test mode
    if '--test' in sys.argv:
        print("Running in TEST mode with sample data...")
        logs = [
            {'timestamp': '2026-01-12 10:00:00', 'action_type': 'EMAIL_ACTION', 'status': 'SUCCESS', 'file': 'test1.md'},
            {'timestamp': '2026-01-12 11:00:00', 'action_type': 'EMAIL_ACTION', 'status': 'SUCCESS', 'file': 'test2.md'},
            {'timestamp': '2026-01-12 12:00:00', 'action_type': 'LINKEDIN_POST', 'status': 'FAILURE', 'file': 'test3.md', 'error': 'API timeout'},
            {'timestamp': '2026-01-12 13:00:00', 'action_type': 'EMAIL_ACTION', 'status': 'SUCCESS', 'file': 'test4.md'},
        ]
    else:
        print("Loading action logs...")
        logs = load_action_logs()
    
    if not logs:
        print("No action logs found. Generating empty report...")
    
    print("Calculating metrics...")
    metrics = calculate_metrics(logs)
    
    print("Generating narrative report...")
    narrative = generate_bezos_narrative(metrics)
    
    print("Saving briefing...")
    save_briefing(narrative)
    
    print("\n✓ Weekly audit complete!")
    print(f"  Total Actions: {metrics['total']}")
    print(f"  Success Rate: {metrics['success_rate']:.1f}%")


if __name__ == "__main__":
    main()
