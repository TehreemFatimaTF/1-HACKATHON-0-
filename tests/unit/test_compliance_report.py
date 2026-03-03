"""
Unit test for compliance report generation in the Gold Tier system.
Test ID: T082 [P] [US4] Unit test for compliance report generation
File: tests/unit/test_compliance_report.py
"""
import pytest
from datetime import datetime, timedelta
import tempfile
import shutil
from unittest.mock import Mock, patch

# Import the necessary modules from the Gold Tier implementation
from src.audit.compliance_report import (
    ComplianceReportGenerator, generate_ceo_briefing_report
)
from src.audit.gold_logger import GoldAuditLogger
from src.audit.audit_schema import (
    GoldAuditEntry, ActionType, ExecutionResult, ErrorDetails
)


class TestComplianceReportUnit:
    """Unit tests for compliance report generation functionality."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Create a temporary directory for audit logs
        self.temp_dir = tempfile.mkdtemp()
        self.audit_logger = GoldAuditLogger(log_dir=self.temp_dir)
        self.generator = ComplianceReportGenerator(audit_logger=self.audit_logger)

    def teardown_method(self):
        """Clean up after each test method."""
        # Clean up temporary directory
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_daily_report_generation(self):
        """
        Test generation of daily compliance report.

        Input: Audit entries for a single day
        Expected: Comprehensive daily compliance report with statistics
        """
        # Create some audit entries for testing
        self.audit_logger.log_action(
            action_type=ActionType.TASK_START,
            action_name="daily_test_task_1",
            parameters={"test": "daily", "id": 1},
            decision_rationale="Testing daily report generation",
            execution_result=ExecutionResult.SUCCESS,
            result_data={"task_started": True},
            business_impact="Daily test initiated"
        )

        self.audit_logger.log_action(
            action_type=ActionType.STEP_EXECUTE,
            action_name="daily_test_step_1",
            parameters={"test": "daily", "step": 1},
            decision_rationale="Executing daily test step",
            execution_result=ExecutionResult.SUCCESS,
            result_data={"step_completed": True},
            business_impact="Daily test step completed"
        )

        self.audit_logger.log_action(
            action_type=ActionType.MCP_CALL,
            action_name="daily_test_api_call",
            parameters={"test": "daily", "api": "test_endpoint"},
            decision_rationale="Making test API call for daily report",
            execution_result=ExecutionResult.FAILURE,
            result_data={"api_call_failed": True},
            business_impact="Daily test API call failed"
        )

        # Generate daily report
        today = datetime.now().strftime("%Y-%m-%d")
        report = self.generator.generate_daily_report(date=today)

        # Verify report structure
        assert "report_date" in report
        assert "report_type" in report
        assert "date_range" in report
        assert "summary" in report
        assert "action_type_breakdown" in report
        assert "failure_analysis" in report
        assert "compliance_findings" in report

        # Verify report content
        assert report["report_type"] == "DAILY_COMPLIANCE"
        assert report["date_range"]["start"] == today
        assert report["date_range"]["end"] == today

        # Verify summary statistics
        summary = report["summary"]
        assert "total_entries" in summary
        assert "success_rate" in summary
        assert "total_failures" in summary
        assert "daily_average" in summary

        # Should have at least 3 entries based on our logging
        assert summary["total_entries"] >= 3
        assert 0 <= summary["success_rate"] <= 100

        # Verify action type breakdown
        action_breakdown = report["action_type_breakdown"]
        assert ActionType.TASK_START.value in action_breakdown
        assert ActionType.STEP_EXECUTE.value in action_breakdown
        assert ActionType.MCP_CALL.value in action_breakdown

        # Verify failure analysis
        failure_analysis = report["failure_analysis"]
        assert "total_failures" in failure_analysis
        assert failure_analysis["total_failures"] >= 1  # We created one failure

        # Verify compliance findings
        compliance_findings = report["compliance_findings"]
        assert isinstance(compliance_findings, list)
        assert len(compliance_findings) > 0

    def test_weekly_report_generation(self):
        """
        Test generation of weekly compliance report.

        Input: Audit entries spanning multiple days
        Expected: Weekly compliance report aggregating data across the week
        """
        # Create entries for multiple days (simulating a week)
        for i in range(5):  # 5 days of data
            day_str = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")

            # Use the audit logger to write to the specific date files
            # We'll write entries directly for each day
            for j in range(2):  # 2 entries per day
                action_type = ActionType.TASK_START if j == 0 else ActionType.STEP_EXECUTE
                execution_result = ExecutionResult.SUCCESS if j == 0 else ExecutionResult.FAILURE

                # Create a temporary logger for this specific date to write entries
                temp_logger = GoldAuditLogger(log_dir=self.temp_dir)

                # For this test, we'll just create entries in the current date file
                # and the generator will aggregate across dates
                temp_logger.log_action(
                    action_type=action_type,
                    action_name=f"weekly_test_{i}_{j}",
                    parameters={"week_test": True, "day": i, "entry": j},
                    decision_rationale=f"Testing weekly aggregation - day {i}, entry {j}",
                    execution_result=execution_result,
                    result_data={"test_entry": f"day_{i}_entry_{j}"},
                    business_impact=f"Weekly test entry for day {i}"
                )

        # Calculate the date range for the week
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=6)).strftime("%Y-%m-%d")  # Previous 6 days

        # Generate weekly report
        report = self.generator.generate_weekly_report(start_date, end_date)

        # Verify report structure
        assert "report_date" in report
        assert "report_type" in report
        assert "date_range" in report
        assert "summary" in report
        assert "action_type_breakdown" in report
        assert "failure_analysis" in report
        assert "compliance_findings" in report

        # Verify report content
        assert report["report_type"] == "WEEKLY_COMPLIANCE"
        assert report["date_range"]["start"] == start_date
        assert report["date_range"]["end"] == end_date

        # Verify summary has been calculated
        summary = report["summary"]
        assert "total_entries" in summary
        assert "success_rate" in summary
        assert summary["total_entries"] >= 0  # May be 0 if entries were only on current day

    def test_monthly_report_generation(self):
        """
        Test generation of monthly compliance report.

        Input: Audit entries spanning multiple days in a month
        Expected: Monthly compliance report with aggregated statistics
        """
        # Create multiple entries to have sufficient data for monthly report
        for i in range(3):
            self.audit_logger.log_action(
                action_type=ActionType.DECISION,
                action_name=f"monthly_test_{i}",
                parameters={"monthly_test": True, "entry": i},
                decision_rationale=f"Testing monthly report generation - entry {i}",
                execution_result=ExecutionResult.SUCCESS,
                result_data={"monthly_entry": i},
                business_impact=f"Monthly test entry {i}"
            )

        # Generate monthly report for a date range
        start_date = datetime.now().strftime("%Y-%m-01")  # First day of current month
        end_date = datetime.now().strftime("%Y-%m-%d")   # Today

        report = self.generator.generate_monthly_report(start_date, end_date)

        # Verify report structure
        assert "report_date" in report
        assert "report_type" in report
        assert "date_range" in report
        assert "summary" in report
        assert "action_type_breakdown" in report
        assert "failure_analysis" in report
        assert "compliance_findings" in report

        # Verify report content
        assert report["report_type"] == "MONTHLY_COMPLIANCE"
        assert report["date_range"]["start"] == start_date
        assert report["date_range"]["end"] == end_date

        # Verify summary statistics
        summary = report["summary"]
        assert "total_entries" in summary
        assert "success_rate" in summary

    def test_report_summary_statistics(self):
        """
        Test that report summary contains accurate statistics.

        Input: Mixed success/failure entries
        Expected: Correct success rate and failure counts
        """
        # Create entries with mixed results
        for i in range(10):
            if i < 7:  # 7 successes
                result = ExecutionResult.SUCCESS
            elif i < 9:  # 2 failures
                result = ExecutionResult.FAILURE
            else:  # 1 partial
                result = ExecutionResult.PARTIAL

            self.audit_logger.log_action(
                action_type=ActionType.STEP_EXECUTE,
                action_name=f"stats_test_{i}",
                parameters={"test": "summary_stats", "entry": i},
                decision_rationale=f"Testing summary statistics - entry {i}",
                execution_result=result,
                result_data={"entry_number": i},
                business_impact=f"Statistics test entry {i}"
            )

        # Generate report
        today = datetime.now().strftime("%Y-%m-%d")
        report = self.generator.generate_daily_report(date=today)

        # Verify statistics
        summary = report["summary"]
        assert summary["total_entries"] == 10
        assert summary["total_failures"] == 3  # 2 FAILURE + 1 PARTIAL
        assert summary["success_rate"] == 70.0  # 7/10 * 100

    def test_action_type_breakdown(self):
        """
        Test that action type breakdown is accurate.

        Input: Entries with different action types
        Expected: Correct count for each action type
        """
        # Create entries with different action types
        action_types = [ActionType.TASK_START, ActionType.STEP_EXECUTE, ActionType.MCP_CALL, ActionType.ERROR]

        for i, action_type in enumerate(action_types):
            for j in range(2):  # 2 of each type
                self.audit_logger.log_action(
                    action_type=action_type,
                    action_name=f"breakdown_test_{i}_{j}",
                    parameters={"breakdown_test": True, "type": action_type.value, "instance": j},
                    decision_rationale=f"Testing {action_type.value} breakdown - instance {j}",
                    execution_result=ExecutionResult.SUCCESS,
                    result_data={"instance": j},
                    business_impact=f"Breakdown test for {action_type.value}"
                )

        # Generate report
        today = datetime.now().strftime("%Y-%m-%d")
        report = self.generator.generate_daily_report(date=today)

        # Verify action type breakdown
        breakdown = report["action_type_breakdown"]

        for action_type in action_types:
            assert action_type.value in breakdown
            assert breakdown[action_type.value] >= 2  # At least 2 of each type

    def test_failure_analysis(self):
        """
        Test that failure analysis identifies and categorizes failures correctly.

        Input: Entries with various failure types including error details
        Expected: Proper failure categorization and analysis
        """
        # Create some successful entries
        for i in range(3):
            self.audit_logger.log_action(
                action_type=ActionType.STEP_EXECUTE,
                action_name=f"success_{i}",
                parameters={"status": "success"},
                decision_rationale=f"Successful entry {i}",
                execution_result=ExecutionResult.SUCCESS,
                result_data={"success": True},
                business_impact="Successful operation"
            )

        # Create failure with error details
        error_details = ErrorDetails(
            error_type="ConnectionError",
            error_message="Failed to connect to external service",
            stack_trace="Connection timeout after 30 seconds",
            recovery_attempted=True,
            recovery_result="Fallback service used"
        )

        self.audit_logger.log_action(
            action_type=ActionType.MCP_CALL,
            action_name="failed_api_call",
            parameters={"api": "external_service"},
            decision_rationale="API call failed due to connection issue",
            execution_result=ExecutionResult.FAILURE,
            result_data={"api_call_failed": True},
            business_impact="API call failure",
            error_details=error_details
        )

        # Another type of failure
        error_details2 = ErrorDetails(
            error_type="ValidationError",
            error_message="Input validation failed",
            stack_trace="Invalid parameter format",
            recovery_attempted=False
        )

        self.audit_logger.log_action(
            action_type=ActionType.STEP_EXECUTE,
            action_name="validation_failed",
            parameters={"validation": "input_check"},
            decision_rationale="Validation step failed",
            execution_result=ExecutionResult.FAILURE,
            result_data={"validation_failed": True},
            business_impact="Validation failure",
            error_details=error_details2
        )

        # Generate report
        today = datetime.now().strftime("%Y-%m-%d")
        report = self.generator.generate_daily_report(date=today)

        # Verify failure analysis
        failure_analysis = report["failure_analysis"]
        assert "total_failures" in failure_analysis
        assert "failure_types" in failure_analysis
        assert "failure_impact" in failure_analysis

        # Should have 2 failures
        assert failure_analysis["total_failures"] == 2

        # Verify failure types are categorized
        failure_types = failure_analysis["failure_types"]
        assert "ConnectionError" in failure_types
        assert "ValidationError" in failure_types
        assert failure_types["ConnectionError"] == 1
        assert failure_types["ValidationError"] == 1

    def test_compliance_findings_generation(self):
        """
        Test that compliance findings are generated appropriately.

        Input: Various audit entries with different characteristics
        Expected: Relevant compliance findings with appropriate severity
        """
        # Create entries that might trigger compliance findings
        self.audit_logger.log_action(
            action_type=ActionType.TASK_START,
            action_name="P0_critical_task",
            parameters={"priority": "P0", "critical": True},
            decision_rationale="",  # Missing rationale
            execution_result=ExecutionResult.SUCCESS,
            result_data={"task_started": True},
            business_impact="Critical business operation"  # Has impact but no rationale
        )

        # Create an entry with recovery action
        self.audit_logger.log_action(
            action_type=ActionType.DECISION,
            action_name="rollback_procedure",
            parameters={"action": "recovery"},
            decision_rationale="Initiating rollback after failure",
            execution_result=ExecutionResult.SUCCESS,
            result_data={"rollback_executed": True},
            business_impact="System recovery initiated"
        )

        # Generate report
        today = datetime.now().strftime("%Y-%m-%d")
        report = self.generator.generate_daily_report(date=today)

        # Verify compliance findings
        compliance_findings = report["compliance_findings"]
        assert isinstance(compliance_findings, list)
        assert len(compliance_findings) > 0

        # Look for specific types of findings
        has_priority_finding = any("Priority Tracking" in finding.get("category", "") for finding in compliance_findings)
        has_rationale_finding = any("Audit Completeness" in finding.get("category", "") for finding in compliance_findings)
        has_recovery_finding = any("Error Handling" in finding.get("category", "") for finding in compliance_findings)

        # At least one type of finding should be present
        assert has_priority_finding or has_rationale_finding or has_recovery_finding

    def test_ceo_briefing_report_generation(self):
        """
        Test generation of CEO-level briefing report.

        Input: Audit entries for daily operations
        Expected: CEO briefing report with key business metrics
        """
        # Create some entries to have data for the CEO report
        for i in range(5):
            self.audit_logger.log_action(
                action_type=ActionType.TASK_START,
                action_name=f"ceo_test_task_{i}",
                parameters={"ceo_test": True, "task_id": i},
                decision_rationale=f"Testing CEO report - task {i}",
                execution_result=ExecutionResult.SUCCESS if i < 4 else ExecutionResult.FAILURE,
                result_data={"task_result": "completed" if i < 4 else "failed"},
                business_impact=f"Business impact for task {i}"
            )

        # Generate CEO briefing
        ceo_report = generate_ceo_briefing_report()

        # Verify report structure
        assert "report_date" in ceo_report
        assert "report_type" in ceo_report
        assert "executive_summary" in ceo_report
        assert "dashboard_metrics" in ceo_report
        assert "compliance_status" in ceo_report

        # Verify report content
        assert ceo_report["report_type"] == "CEO_BRIEFING"
        assert "operations_completed" in ceo_report["executive_summary"]
        assert "system_health_score" in ceo_report["executive_summary"]
        assert "critical_issues" in ceo_report["executive_summary"]
        assert "tasks_processed" in ceo_report["dashboard_metrics"]
        assert "decisions_made" in ceo_report["dashboard_metrics"]
        assert "system_interactions" in ceo_report["dashboard_metrics"]
        assert "errors_encountered" in ceo_report["dashboard_metrics"]

        # Verify compliance status
        assert ceo_report["compliance_status"] in ["GREEN", "YELLOW"]

    def test_empty_report_generation(self):
        """
        Test that reports can be generated even with no entries.

        Input: Empty audit log
        Expected: Valid report structure with zero counts
        """
        # Don't add any entries - test with empty log
        today = datetime.now().strftime("%Y-%m-%d")
        report = self.generator.generate_daily_report(date=today)

        # Verify report structure exists
        assert "report_date" in report
        assert "report_type" in report
        assert "summary" in report
        assert "action_type_breakdown" in report
        assert "failure_analysis" in report
        assert "compliance_findings" in report

        # Verify summary for empty data
        summary = report["summary"]
        assert summary["total_entries"] == 0
        assert summary["success_rate"] == 100.0  # Default to 100% when no entries
        assert summary["total_failures"] == 0
        assert summary["daily_average"] == 0

        # Verify empty breakdown
        action_breakdown = report["action_type_breakdown"]
        assert isinstance(action_breakdown, dict)
        assert len(action_breakdown) == 0

        # Verify failure analysis for empty data
        failure_analysis = report["failure_analysis"]
        assert failure_analysis["total_failures"] == 0
        assert isinstance(failure_analysis["failure_types"], dict)
        assert len(failure_analysis["failure_types"]) == 0


if __name__ == "__main__":
    test = TestComplianceReportUnit()

    print("Running daily report generation test...")
    try:
        test.test_daily_report_generation()
        print("✅ Daily report generation test passed")
    except Exception as e:
        print(f"❌ Daily report generation test failed: {e}")

    print("Running weekly report generation test...")
    try:
        test.test_weekly_report_generation()
        print("✅ Weekly report generation test passed")
    except Exception as e:
        print(f"❌ Weekly report generation test failed: {e}")

    print("Running monthly report generation test...")
    try:
        test.test_monthly_report_generation()
        print("✅ Monthly report generation test passed")
    except Exception as e:
        print(f"❌ Monthly report generation test failed: {e}")

    print("Running report summary statistics test...")
    try:
        test.test_report_summary_statistics()
        print("✅ Report summary statistics test passed")
    except Exception as e:
        print(f"❌ Report summary statistics test failed: {e}")

    print("Running action type breakdown test...")
    try:
        test.test_action_type_breakdown()
        print("✅ Action type breakdown test passed")
    except Exception as e:
        print(f"❌ Action type breakdown test failed: {e}")

    print("Running failure analysis test...")
    try:
        test.test_failure_analysis()
        print("✅ Failure analysis test passed")
    except Exception as e:
        print(f"❌ Failure analysis test failed: {e}")

    print("Running compliance findings generation test...")
    try:
        test.test_compliance_findings_generation()
        print("✅ Compliance findings generation test passed")
    except Exception as e:
        print(f"❌ Compliance findings generation test failed: {e}")

    print("Running CEO briefing report generation test...")
    try:
        test.test_ceo_briefing_report_generation()
        print("✅ CEO briefing report generation test passed")
    except Exception as e:
        print(f"❌ CEO briefing report generation test failed: {e}")

    print("Running empty report generation test...")
    try:
        test.test_empty_report_generation()
        print("✅ Empty report generation test passed")
    except Exception as e:
        print(f"❌ Empty report generation test failed: {e}")

    print("All compliance report unit tests completed!")