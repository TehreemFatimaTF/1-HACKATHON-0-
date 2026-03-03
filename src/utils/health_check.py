"""
Health Check Utility for Gold Tier Autonomous Employee

Validates all MCP server connections and system components before starting
autonomous operations. Part of T099 - Quickstart validation script.

Usage:
    python src/utils/health_check.py

Returns:
    Exit code 0 if all checks pass, 1 if any check fails
"""

import os
import sys
from typing import Dict, List, Tuple
from pathlib import Path
from dotenv import load_dotenv
import json

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.mcp.odoo_client import OdooClient
from src.mcp.twitter_client import TwitterClient
from src.mcp.facebook_client import FacebookClient
from src.mcp.instagram_client import InstagramClient

load_dotenv()


class HealthChecker:
    """System health validation for all MCP servers and components"""

    def __init__(self):
        self.results: List[Tuple[str, bool, str]] = []
        self.critical_failures = 0
        self.warnings = 0

    def check_environment_variables(self) -> bool:
        """Verify all required environment variables are set"""
        print("Checking environment variables...")

        required_vars = {
            "ODOO_URL": "Odoo server URL",
            "ODOO_DB": "Odoo database name",
            "ODOO_USERNAME": "Odoo username",
            "ODOO_PASSWORD": "Odoo password",
        }

        optional_vars = {
            "TWITTER_API_KEY": "Twitter API credentials",
            "FACEBOOK_APP_ID": "Facebook API credentials",
            "INSTAGRAM_BUSINESS_ACCOUNT_ID": "Instagram API credentials",
        }

        all_present = True

        # Check required variables
        for var, description in required_vars.items():
            value = os.getenv(var)
            if not value or value.startswith("your_"):
                print(f"   ❌ Missing: {var} ({description})")
                self.results.append((var, False, f"Required variable not set"))
                self.critical_failures += 1
                all_present = False
            else:
                print(f"   ✅ {var}: Configured")
                self.results.append((var, True, "OK"))

        # Check optional variables (warnings only)
        for var, description in optional_vars.items():
            value = os.getenv(var)
            if not value or value.startswith("your_"):
                print(f"   ⚠️  Optional: {var} ({description}) - Not configured")
                self.warnings += 1
            else:
                print(f"   ✅ {var}: Configured")

        return all_present

    def check_odoo_connection(self) -> bool:
        """Test Odoo server connectivity"""
        print("\n🔍 Checking Odoo connection...")

        try:
            client = OdooClient(
                url=os.getenv("ODOO_URL", "http://localhost:8069"),
                db=os.getenv("ODOO_DB", "odoo"),
                username=os.getenv("ODOO_USERNAME", "admin"),
                password=os.getenv("ODOO_PASSWORD", "admin")
            )

            health = client.health_check()

            if health["status"] == "healthy":
                print(f"   ✅ Odoo connection successful")
                print(f"      Server: {health.get('server', 'N/A')}")
                print(f"      Database: {health.get('database', 'N/A')}")
                self.results.append(("Odoo", True, "Connected"))
                return True
            else:
                error = health.get("error", "Unknown error")
                print(f"   ❌ Odoo connection failed: {error}")
                self.results.append(("Odoo", False, error))
                self.critical_failures += 1
                return False

        except Exception as e:
            print(f"   ❌ Odoo connection error: {e}")
            self.results.append(("Odoo", False, str(e)))
            self.critical_failures += 1
            return False

    def check_twitter_connection(self) -> bool:
        """Test Twitter/X API connectivity"""
        print("\n🔍 Checking Twitter/X connection...")

        api_key = os.getenv("TWITTER_API_KEY")
        if not api_key or api_key.startswith("your_"):
            print("   ⚠️  Twitter credentials not configured (optional)")
            self.warnings += 1
            return True  # Not critical

        try:
            client = TwitterClient(
                api_key=api_key,
                api_secret=os.getenv("TWITTER_API_SECRET"),
                access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
                access_token_secret=os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
            )

            health = client.health_check()

            if health["status"] == "healthy":
                print(f"   ✅ Twitter connection successful")
                self.results.append(("Twitter", True, "Connected"))
                return True
            else:
                print(f"   ⚠️  Twitter connection failed: {health.get('error')}")
                self.warnings += 1
                return True  # Not critical

        except Exception as e:
            print(f"   ⚠️  Twitter connection error: {e}")
            self.warnings += 1
            return True  # Not critical

    def check_directory_structure(self) -> bool:
        """Verify all required directories exist"""
        print("\n🔍 Checking directory structure...")

        required_dirs = [
            "Inbox",
            "Needs_Action",
            "Plans",
            "4_Approved",
            "Done",
            "Logs",
            "Logs/Audit_Trail",
            "Memory",
            "src/mcp",
            "src/skills",
            "src/audit",
            "tests/contract",
            "tests/integration",
            "tests/unit"
        ]

        all_exist = True

        for dir_path in required_dirs:
            full_path = project_root / dir_path
            if full_path.exists():
                print(f"   ✅ {dir_path}")
            else:
                print(f"   ❌ Missing: {dir_path}")
                self.results.append((f"Dir: {dir_path}", False, "Directory not found"))
                self.critical_failures += 1
                all_exist = False

        return all_exist

    def check_audit_log_integrity(self) -> bool:
        """Verify audit log files are accessible and valid"""
        print("\n🔍 Checking audit log integrity...")

        audit_dir = project_root / "Logs" / "Audit_Trail"

        if not audit_dir.exists():
            print("   ❌ Audit directory not found")
            self.critical_failures += 1
            return False

        # Check for recent audit logs
        audit_files = list(audit_dir.glob("gold_audit_*.jsonl"))

        if not audit_files:
            print("   ⚠️  No audit logs found (expected for new installation)")
            self.warnings += 1
            return True

        print(f"   ✅ Found {len(audit_files)} audit log file(s)")

        # Verify latest log is readable
        latest_log = max(audit_files, key=lambda p: p.stat().st_mtime)
        try:
            with open(latest_log, 'r') as f:
                lines = f.readlines()
                if lines:
                    # Verify JSON format
                    json.loads(lines[-1])
                    print(f"   ✅ Latest audit log is valid ({len(lines)} entries)")
                else:
                    print("   ⚠️  Latest audit log is empty")
                    self.warnings += 1
        except Exception as e:
            print(f"   ❌ Audit log validation failed: {e}")
            self.critical_failures += 1
            return False

        return True

    def check_mcp_connection_tracker(self) -> bool:
        """Verify MCP connection tracker file exists"""
        print("\n🔍 Checking MCP connection tracker...")

        tracker_file = project_root / "Memory" / "mcp_connections.json"

        if not tracker_file.exists():
            print("   ⚠️  MCP connection tracker not found (will be created on first run)")
            self.warnings += 1
            return True

        try:
            with open(tracker_file, 'r') as f:
                data = json.load(f)
                print(f"   ✅ MCP tracker valid ({len(data)} connections tracked)")
                return True
        except Exception as e:
            print(f"   ❌ MCP tracker validation failed: {e}")
            self.critical_failures += 1
            return False

    def run_all_checks(self) -> bool:
        """Run all health checks and return overall status"""
        print("=" * 60)
        print("Gold Tier System Health Check")
        print("=" * 60)

        checks = [
            self.check_environment_variables,
            self.check_directory_structure,
            self.check_odoo_connection,
            self.check_twitter_connection,
            self.check_audit_log_integrity,
            self.check_mcp_connection_tracker,
        ]

        for check in checks:
            check()

        # Print summary
        print("\n" + "=" * 60)
        print("Health Check Summary")
        print("=" * 60)

        if self.critical_failures == 0:
            print(f"[OK] All critical checks passed!")
            if self.warnings > 0:
                print(f"[WARN] {self.warnings} warning(s) - optional features not configured")
            print("\n[READY] System is ready for autonomous operations!")
            return True
        else:
            print(f"[FAIL] {self.critical_failures} critical failure(s) detected")
            if self.warnings > 0:
                print(f"[WARN] {self.warnings} warning(s)")
            print("\n[NOT READY] System is NOT ready. Please fix critical issues before starting.")
            return False


def main():
    """Main entry point for health check"""
    checker = HealthChecker()
    success = checker.run_all_checks()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
