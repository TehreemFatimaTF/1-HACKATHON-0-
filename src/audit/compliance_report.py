"""
Compliance Report Generator
Generates compliance reports from audit trail data for governance and oversight
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path
import json

from src.audit.gold_logger import GoldAuditLogger
from src.audit.audit_schema import GoldAuditEntry, ActionType, ExecutionResult


class ComplianceReportGenerator:
    """
    Generates compliance reports from audit trail data.

    Provides insights into autonomous system operations for governance and oversight.
    """

    def __init__(self, audit_logger: Optional[GoldAuditLogger] = None):
        self.audit_logger = audit_logger or GoldAuditLogger()

    def generate_daily_report(self, date: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate daily compliance report.

        Args:
            date: Date in YYYY-MM-DD format (defaults to today)

        Returns:
            Compliance report with statistics and findings
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        entries = self.audit_logger.read_entries(date=date)

        return {
            "report_date": datetime.now().isoformat() + "Z",
            "report_type": "DAILY_COMPLIANCE",
            "date_range": {"start": date, "end": date},
            "summary": self._generate_summary(entries),
            "action_type_breakdown": self._generate_action_type_breakdown(entries),
            "failure_analysis": self._generate_failure_analysis(entries),
            "compliance_findings": self._generate_compliance_findings(entries)
        }

    def generate_weekly_report(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """
        Generate weekly compliance report.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            Weekly compliance report with statistics and findings
        """
        # For weekly report, we'll aggregate day by day for the week
        entries = []
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")

        current = start
        while current <= end:
            day_entries = self.audit_logger.read_entries(date=current.strftime("%Y-%m-%d"))
            entries.extend(day_entries)
            current += timedelta(days=1)

        return {
            "report_date": datetime.now().isoformat() + "Z",
            "report_type": "WEEKLY_COMPLIANCE",
            "date_range": {"start": start_date, "end": end_date},
            "summary": self._generate_summary(entries),
            "action_type_breakdown": self._generate_action_type_breakdown(entries),
            "failure_analysis": self._generate_failure_analysis(entries),
            "compliance_findings": self._generate_compliance_findings(entries)
        }

    def generate_monthly_report(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """
        Generate monthly compliance report.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            Monthly compliance report with statistics and findings
        """
        # Similar to weekly but for longer period
        entries = []
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")

        current = start
        while current <= end:
            day_entries = self.audit_logger.read_entries(date=current.strftime("%Y-%m-%d"))
            entries.extend(day_entries)
            current += timedelta(days=1)

        return {
            "report_date": datetime.now().isoformat() + "Z",
            "report_type": "MONTHLY_COMPLIANCE",
            "date_range": {"start": start_date, "end": end_date},
            "summary": self._generate_summary(entries),
            "action_type_breakdown": self._generate_action_type_breakdown(entries),
            "failure_analysis": self._generate_failure_analysis(entries),
            "compliance_findings": self._generate_compliance_findings(entries)
        }

    def _generate_summary(self, entries: List[GoldAuditEntry]) -> Dict[str, Any]:
        """Generate summary statistics for the report."""
        if not entries:
            return {
                "total_entries": 0,
                "success_rate": 100.0,
                "total_failures": 0,
                "daily_average": 0
            }

        total_entries = len(entries)
        successful_entries = len([e for e in entries if e.execution_result == ExecutionResult.SUCCESS])
        failed_entries = len([e for e in entries if e.execution_result == ExecutionResult.FAILURE])

        success_rate = (successful_entries / total_entries) * 100 if total_entries > 0 else 100.0

        # Calculate daily average (assuming these are from one day)
        date_counts = {}
        for entry in entries:
            date = entry.timestamp.split('T')[0]  # Extract date part
            date_counts[date] = date_counts.get(date, 0) + 1

        avg_daily_entries = sum(date_counts.values()) / len(date_counts) if date_counts else 0

        return {
            "total_entries": total_entries,
            "success_rate": round(success_rate, 2),
            "total_failures": failed_entries,
            "daily_average": round(avg_daily_entries, 2)
        }

    def _generate_action_type_breakdown(self, entries: List[GoldAuditEntry]) -> Dict[str, int]:
        """Generate breakdown by action type."""
        breakdown = {}
        for entry in entries:
            action_type = entry.action_type.value
            breakdown[action_type] = breakdown.get(action_type, 0) + 1
        return breakdown

    def _generate_failure_analysis(self, entries: List[GoldAuditEntry]) -> Dict[str, Any]:
        """Analyze failures in the audit entries."""
        failures = [e for e in entries if e.execution_result in [ExecutionResult.FAILURE, ExecutionResult.PARTIAL]]

        if not failures:
            return {
                "total_failures": 0,
                "failure_types": {},
                "failure_impact": "No failures detected"
            }

        failure_types = {}
        for failure in failures:
            error_type = "Unknown"
            if failure.error_details and failure.error_details.error_type:
                error_type = failure.error_details.error_type
            failure_types[error_type] = failure_types.get(error_type, 0) + 1

        return {
            "total_failures": len(failures),
            "failure_types": failure_types,
            "failure_impact": f"{len(failures)} failures detected that may require attention"
        }

    def _generate_compliance_findings(self, entries: List[GoldAuditEntry]) -> List[Dict[str, str]]:
        """Generate compliance findings based on audit entries."""
        findings = []

        # Check for potentially non-compliant patterns
        high_priority_tasks = [e for e in entries if "P0" in e.action_name or "P1" in e.action_name]
        if high_priority_tasks:
            findings.append({
                "severity": "INFO",
                "category": "Priority Tracking",
                "description": f"Detected {len(high_priority_tasks)} high-priority task operations"
            })

        # Check for missing decision rationales (if business_impact exists but no rationale)
        missing_rationales = [e for e in entries
                            if e.business_impact and not e.decision_rationale.strip()]
        if missing_rationales:
            findings.append({
                "severity": "WARNING",
                "category": "Audit Completeness",
                "description": f"Found {len(missing_rationales)} entries with business impact but no decision rationale"
            })

        # Check for error recovery patterns
        recovery_operations = [e for e in entries if "recovery" in e.action_name.lower() or
                              "rollback" in e.action_name.lower()]
        if recovery_operations:
            findings.append({
                "severity": "INFO",
                "category": "Error Handling",
                "description": f"Detected {len(recovery_operations)} error recovery/rollback operations"
            })

        # If no findings, add a compliance confirmation
        if not findings:
            findings.append({
                "severity": "INFO",
                "category": "General",
                "description": "No significant compliance concerns detected in audit trail"
            })

        return findings


def generate_ceo_briefing_report() -> Dict[str, Any]:
    """
    Generate a CEO-level briefing report focusing on business metrics.

    Returns:
        CEO briefing report with key business metrics and insights
    """
    audit_logger = GoldAuditLogger()
    generator = ComplianceReportGenerator(audit_logger)

    # Generate daily report by default
    daily_report = generator.generate_daily_report()

    # Create CEO-level summary
    ceo_report = {
        "report_date": datetime.now().isoformat() + "Z",
        "report_type": "CEO_BRIEFING",
        "executive_summary": {
            "operations_completed": daily_report["summary"]["total_entries"],
            "system_health_score": daily_report["summary"]["success_rate"],
            "critical_issues": daily_report["failure_analysis"]["total_failures"],
            "key_business_impact": "Autonomous system operational with {0}% success rate".format(
                daily_report["summary"]["success_rate"]
            )
        },
        "dashboard_metrics": {
            "tasks_processed": sum(1 for k, v in daily_report["action_type_breakdown"].items()
                                 if k in ["TASK_START", "TASK_COMPLETE"]),
            "decisions_made": daily_report["action_type_breakdown"].get("DECISION", 0),
            "system_interactions": daily_report["action_type_breakdown"].get("MCP_CALL", 0),
            "errors_encountered": daily_report["failure_analysis"]["total_failures"]
        },
        "compliance_status": "GREEN" if daily_report["failure_analysis"]["total_failures"] == 0 else "YELLOW",
        "action_required": None,
        "trends": "System operating within expected parameters"
    }

    if daily_report["failure_analysis"]["total_failures"] > 0:
        ceo_report["action_required"] = f"Review {daily_report['failure_analysis']['total_failures']} failures"
        ceo_report["compliance_status"] = "YELLOW"

    return ceo_report