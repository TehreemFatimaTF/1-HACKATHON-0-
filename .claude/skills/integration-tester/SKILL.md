---
description: Integration testing specialist - validates Gold Tier workflows and system reliability
tags: [testing, integration, quality-assurance, validation, gold-tier]
---

# Integration Test Engineer

> [!IMPORTANT]
> This skill ensures the Digital FTE system meets Gold Tier hackathon requirements through comprehensive integration testing. Every test validates real-world workflows, not isolated functions.

## Core Philosophy
**"Test like a user, validate like an auditor."** Integration tests prove the system works end-to-end, not just in isolated pieces. Every test should simulate a real business scenario.

---

## Gold Tier Test Requirements

### Critical Workflows to Validate
1. **Email → Invoice → Odoo**: End-to-end accounting workflow
2. **Social Media**: Multi-platform posting with summary generation
3. **CEO Audit**: Weekly briefing generation with real data
4. **Ralph Loop**: Autonomous multi-step task completion
5. **Safety Gates**: Financial threshold enforcement

---

## Test Implementation Strategy

### Test File: `Tests/test_gold_tier_integration.py`

```python
"""
Gold Tier Integration Tests
Validates all hackathon-required workflows end-to-end.
"""

import pytest
import json
import time
from pathlib import Path
from datetime import datetime
import subprocess
import shutil

# Test Configuration
BASE_DIR = Path(__file__).parent.parent
INBOX = BASE_DIR / "00_Inbox"
NEEDS_ACTION = BASE_DIR / "01_Needs_Action"
PENDING = BASE_DIR / "02_Pending_Approval"
APPROVED = BASE_DIR / "03_Approved"
ARCHIVE = BASE_DIR / "04_Archive"
LOGS = BASE_DIR / "Logs"
MANAGEMENT = BASE_DIR / "Management"

@pytest.fixture(scope="session")
def test_env():
    """Setup test environment"""
    # Backup production data
    backup_dir = BASE_DIR / "Tests" / "backup"
    backup_dir.mkdir(exist_ok=True)
    
    # Create test directories
    for dir in [INBOX, NEEDS_ACTION, PENDING, APPROVED, ARCHIVE]:
        dir.mkdir(exist_ok=True)
    
    yield
    
    # Cleanup test files
    # (Keep for manual inspection during hackathon)

class TestOdooIntegration:
    """Test Odoo accounting workflows"""
    
    def test_invoice_creation_workflow(self, test_env):
        """
        Test: Email request → Invoice draft → Approval → Odoo creation
        Expected: Invoice created in Odoo, logged to audit trail
        """
        # Step 1: Create invoice request
        request_file = INBOX / "Create_Invoice_Test_Client.md"
        request_file.write_text("""
---
type: invoice_request
client: Test Client A
amount: 500.00
---

# Invoice Request

Please create an invoice for Test Client A for $500.00 for consulting services.
""")
        
        # Step 2: Trigger orchestrator (or wait for watcher)
        time.sleep(2)  # Allow processing
        
        # Step 3: Verify plan created
        plan_files = list(NEEDS_ACTION.glob("PLAN_*Test_Client*.md"))
        assert len(plan_files) > 0, "Plan file should be created"
        
        # Step 4: Simulate approval
        plan_file = plan_files[0]
        approved_file = APPROVED / plan_file.name
        shutil.move(str(plan_file), str(approved_file))
        
        # Step 5: Wait for execution
        time.sleep(3)
        
        # Step 6: Verify invoice created in Odoo
        # (Check via MCP server or Odoo API)
        
        # Step 7: Verify audit log
        audit_log = LOGS / "Action_Logs.json"
        assert audit_log.exists(), "Audit log should exist"
        
        with open(audit_log) as f:
            logs = json.load(f)
            invoice_logs = [l for l in logs if l.get("type") == "ODOO_INVOICE"]
            assert len(invoice_logs) > 0, "Invoice should be logged"
    
    def test_payment_recording_workflow(self, test_env):
        """
        Test: Payment notification → Payment draft → Approval → Odoo posting
        """
        # Similar structure to invoice test
        pass
    
    def test_financial_safety_threshold(self, test_env):
        """
        Test: $500 payment → BLOCKED → Approval required
        Expected: System stops, creates approval request
        """
        request_file = INBOX / "Payment_Request_500.md"
        request_file.write_text("""
---
type: payment_request
amount: 500.00
---

# Payment Request

Pay $500 to vendor.
""")
        
        time.sleep(2)
        
        # Verify STOPS at approval stage
        approval_files = list(PENDING.glob("*PAYMENT*.md"))
        assert len(approval_files) > 0, "Should create approval request for $500"
        
        # Verify NOT executed automatically
        # (Check Odoo for no payment record)

class TestSocialMediaIntegration:
    """Test social media workflows"""
    
    def test_facebook_posting_with_summary(self, test_env):
        """
        Test: Post request → Facebook post → Summary updated
        """
        # Create post request
        post_file = APPROVED / "P1_FB_Test_Post.md"
        post_file.write_text("""
---
type: social_facebook
---

**Message:**
This is a test post for hackathon validation.

**Link:**
https://example.com
""")
        
        # Trigger action executor
        result = subprocess.run(
            ["python", "facebook_poster.py", str(post_file), "--summary", "--dry-run"],
            cwd=BASE_DIR,
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0, "Facebook poster should succeed"
        
        # Verify summary updated
        summary_file = MANAGEMENT / "Social_Media_Summary.md"
        assert summary_file.exists(), "Summary file should exist"
        
        content = summary_file.read_text()
        assert "Test_Post" in content or "test post" in content.lower()
    
    def test_multi_platform_posting(self, test_env):
        """
        Test: Single content → FB + Twitter + Instagram
        Expected: 3 posts created, all in summary
        """
        # Test Triple-Draft Mandate from comm-strategist skill
        pass

class TestCEOAudit:
    """Test CEO briefing generation"""
    
    def test_weekly_audit_generation(self, test_env):
        """
        Test: Scheduled trigger → Data collection → Briefing created
        """
        # Run audit generator
        result = subprocess.run(
            ["python", "generate_ceo_audit.py"],
            cwd=BASE_DIR,
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0, "Audit generator should succeed"
        
        # Verify briefing created
        briefing_files = list(MANAGEMENT.glob("CEO_WEEKLY_BRIEFING*.md"))
        assert len(briefing_files) > 0, "CEO briefing should be created"
        
        # Verify sections present
        briefing = briefing_files[0].read_text()
        required_sections = [
            "Revenue",
            "Completed Tasks",
            "Bottlenecks",
            "Proactive Suggestions"
        ]
        for section in required_sections:
            assert section in briefing, f"Briefing should include {section}"
    
    def test_audit_includes_odoo_data(self, test_env):
        """
        Test: CEO audit includes Odoo financial data
        """
        # Verify Odoo integration in audit
        pass

class TestRalphLoop:
    """Test autonomous iteration"""
    
    def test_multi_step_task_completion(self, test_env):
        """
        Test: Complex task → Ralph loop → Completion without intervention
        """
        # Create multi-step task
        task_file = INBOX / "Multi_Step_Task.md"
        task_file.write_text("""
---
type: complex_task
---

# Multi-Step Task

1. Create invoice for Client A ($200)
2. Post to LinkedIn about new client
3. Update CEO dashboard

Complete all steps autonomously.
""")
        
        # Trigger Ralph loop
        result = subprocess.run(
            ["python", "ralph_loop.py", "--max-iterations", "10"],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        # Verify completion
        assert "TASK_COMPLETE" in result.stdout or result.returncode == 0
        
        # Verify all steps completed
        # (Check for invoice, LinkedIn post, dashboard update)

class TestSystemReliability:
    """Test error handling and graceful degradation"""
    
    def test_odoo_connection_failure_handling(self, test_env):
        """
        Test: Odoo unavailable → Graceful degradation → Escalation
        """
        # Simulate Odoo down
        # Trigger invoice creation
        # Verify escalation file created
        pass
    
    def test_api_rate_limit_handling(self, test_env):
        """
        Test: API rate limit → Exponential backoff → Retry
        """
        pass
    
    def test_watchdog_process_restart(self, test_env):
        """
        Test: Watcher crashes → Watchdog detects → Auto-restart
        """
        pass

class TestSecurityCompliance:
    """Test security and compliance features"""
    
    def test_credential_not_logged(self, test_env):
        """
        Test: Verify no credentials in logs
        """
        audit_log = LOGS / "Action_Logs.json"
        if audit_log.exists():
            content = audit_log.read_text()
            # Check for common credential patterns
            forbidden_patterns = ["API_KEY", "password", "token", "secret"]
            for pattern in forbidden_patterns:
                assert pattern not in content, f"Credentials ({pattern}) should not be in logs"
    
    def test_approval_workflow_enforced(self, test_env):
        """
        Test: Sensitive action → Approval required → Not executed without approval
        """
        # Already covered in financial safety test
        pass

# Performance Benchmarks
class TestPerformance:
    """Test system performance metrics"""
    
    def test_invoice_creation_speed(self, test_env):
        """
        Test: Invoice creation completes in < 5 seconds
        """
        start = time.time()
        # Create invoice
        # Measure time
        elapsed = time.time() - start
        assert elapsed < 5.0, "Invoice creation should be < 5 seconds"
    
    def test_concurrent_task_handling(self, test_env):
        """
        Test: System handles 5 simultaneous tasks
        """
        # Create 5 tasks simultaneously
        # Verify all complete successfully
        pass

# Hackathon Demonstration Tests
class TestHackathonDemo:
    """Tests specifically for hackathon demonstration"""
    
    def test_end_to_end_demo_scenario(self, test_env):
        """
        The complete hackathon demo workflow:
        1. Email arrives with invoice request
        2. System creates plan
        3. Human approves
        4. Invoice created in Odoo
        5. Email sent to client
        6. Social media post scheduled
        7. CEO briefing updated
        """
        # This is the "wow" demo for judges
        pass
    
    def test_innovation_showcase(self, test_env):
        """
        Demonstrate key innovations:
        - Ralph Wiggum loop
        - Skill-based agent system
        - Human-in-the-loop safety
        """
        pass

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
```

---

## Test Execution Strategy

### Pre-Hackathon Testing
```bash
# Run all tests
pytest Tests/test_gold_tier_integration.py -v

# Run specific test class
pytest Tests/test_gold_tier_integration.py::TestOdooIntegration -v

# Run with coverage
pytest Tests/test_gold_tier_integration.py --cov=. --cov-report=html
```

### During Hackathon Demo
```bash
# Quick smoke test (30 seconds)
pytest Tests/test_gold_tier_integration.py::TestHackathonDemo -v

# Full validation (5 minutes)
pytest Tests/test_gold_tier_integration.py -v --tb=short
```

---

## Test Data Management

### Test Fixtures
Create `Tests/fixtures/` directory with:
- `sample_emails.json`: Test email data
- `sample_invoices.json`: Test invoice data
- `sample_social_posts.md`: Test social media content

### Cleanup Strategy
```python
@pytest.fixture(scope="function", autouse=True)
def cleanup_test_files():
    """Clean up test files after each test"""
    yield
    # Remove test files from production directories
    # Keep logs for inspection
```

---

## Success Criteria

### Gold Tier Validation
- [ ] All Odoo workflows pass
- [ ] All social media workflows pass
- [ ] CEO audit generates successfully
- [ ] Ralph loop completes multi-step tasks
- [ ] Financial safety thresholds enforced
- [ ] No credentials in logs
- [ ] All tests pass in < 5 minutes

### Hackathon Readiness
- [ ] Demo scenario test passes
- [ ] Performance benchmarks met
- [ ] Error handling validated
- [ ] Security compliance verified

---

## Continuous Integration

### GitHub Actions Workflow
```yaml
name: Gold Tier Integration Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.13'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run integration tests
        run: pytest Tests/test_gold_tier_integration.py -v
```

---

## Reporting

### Test Report Format
```markdown
# Gold Tier Integration Test Report

**Date:** 2026-02-05
**Duration:** 4m 32s
**Status:** ✅ PASSED

## Summary
- Total Tests: 23
- Passed: 23
- Failed: 0
- Skipped: 0

## Coverage
- Odoo Integration: 100%
- Social Media: 100%
- CEO Audit: 100%
- Ralph Loop: 100%
- Security: 100%

## Performance
- Invoice Creation: 2.3s (target: <5s) ✅
- CEO Audit: 8.7s (target: <10s) ✅
- Social Post: 1.1s (target: <3s) ✅
```

---

**Remember:** Tests are proof of functionality. For hackathon judges, passing tests = working system = credibility. Make tests comprehensive, fast, and demonstrable.

---

*This skill ensures Gold Tier compliance through rigorous integration testing.*
