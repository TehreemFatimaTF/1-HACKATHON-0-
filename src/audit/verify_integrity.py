"""
Audit Log Integrity Verification
Provides functions for verifying the integrity of audit logs with tamper detection
Test ID: T087 [US4] Implement audit log integrity verification
File: src/audit/verify_integrity.py
"""
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any
import json
import hashlib
from datetime import datetime

from src.audit.audit_schema import GoldAuditEntry, verify_audit_chain


def verify_single_entry_integrity(entry: GoldAuditEntry) -> Tuple[bool, Optional[str]]:
    """
    Verify the integrity of a single audit entry by checking its hash.

    Args:
        entry: The audit entry to verify

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        is_valid = entry.verify_hash()
        if not is_valid:
            return False, f"Entry hash verification failed for entry {entry.entry_id}"
        return True, None
    except Exception as e:
        return False, f"Exception during entry verification: {str(e)}"


def verify_log_file_integrity(log_file_path: Path) -> Tuple[bool, Optional[str], Dict[str, Any]]:
    """
    Verify the integrity of an entire audit log file.

    Args:
        log_file_path: Path to the audit log file (.jsonl)

    Returns:
        Tuple of (is_valid, error_message, metadata)
        Metadata contains statistics about the verification process
    """
    if not log_file_path.exists():
        return True, "Log file does not exist, verification skipped", {
            "total_entries": 0,
            "verified_entries": 0,
            "tampered_entries": 0,
            "file_exists": False
        }

    entries = []
    invalid_entry_ids = []

    try:
        # Read all entries from the log file
        with open(log_file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue

                try:
                    entry = GoldAuditEntry.from_json(line)
                    entries.append(entry)

                    # Verify each entry's individual hash
                    if not entry.verify_hash():
                        invalid_entry_ids.append((line_num, entry.entry_id, "hash_verification_failed"))
                except Exception as e:
                    return False, f"Failed to parse entry at line {line_num}: {str(e)}", {
                        "total_entries": len(entries),
                        "verified_entries": len(entries),
                        "tampered_entries": len(invalid_entry_ids),
                        "file_exists": True
                    }

        # Now verify the chain integrity
        if not entries:
            return True, "No entries to verify", {
                "total_entries": 0,
                "verified_entries": 0,
                "tampered_entries": 0,
                "file_exists": True
            }

        chain_valid, chain_error = verify_audit_chain(entries)

        metadata = {
            "total_entries": len(entries),
            "verified_entries": len(entries) - len(invalid_entry_ids),
            "tampered_entries": len(invalid_entry_ids),
            "file_exists": True,
            "individual_hash_failures": len(invalid_entry_ids),
            "chain_integrity": chain_valid
        }

        if invalid_entry_ids:
            error_msg = f"Found {len(invalid_entry_ids)} entries with invalid hashes: {invalid_entry_ids[:5]}"  # Limit error length
            if len(invalid_entry_ids) > 5:
                error_msg += f" ... and {len(invalid_entry_ids) - 5} more"
            return False, error_msg, metadata

        if not chain_valid:
            return False, f"Chain integrity failed: {chain_error}", metadata

        return True, "Log file integrity verified successfully", metadata

    except Exception as e:
        return False, f"Exception during log file verification: {str(e)}", {
            "total_entries": len(entries),
            "verified_entries": len([e for e in entries if e.verify_hash()]),
            "tampered_entries": len(invalid_entry_ids),
            "file_exists": True,
            "error": str(e)
        }


def verify_date_range_integrity(start_date: str, end_date: str, log_dir: str = "Logs/Audit_Trail") -> Dict[str, Any]:
    """
    Verify integrity of audit logs for a date range.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        log_dir: Directory containing audit logs

    Returns:
        Dictionary with verification results for each date and overall summary
    """
    from datetime import datetime, timedelta
    import os

    log_dir_path = Path(log_dir)
    results = {
        "verification_date": datetime.now().isoformat(),
        "date_range": {"start": start_date, "end": end_date},
        "individual_results": {},
        "summary": {
            "total_files": 0,
            "valid_files": 0,
            "invalid_files": 0,
            "total_entries": 0,
            "valid_entries": 0,
            "tampered_entries": 0
        }
    }

    # Parse dates
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    current = start
    while current <= end:
        date_str = current.strftime("%Y-%m-%d")
        log_file_path = log_dir_path / f"gold_audit_{date_str}.jsonl"

        is_valid, error_msg, metadata = verify_log_file_integrity(log_file_path)

        results["individual_results"][date_str] = {
            "is_valid": is_valid,
            "error": error_msg,
            "metadata": metadata
        }

        # Update summary
        results["summary"]["total_files"] += 1
        if is_valid:
            results["summary"]["valid_files"] += 1
        else:
            results["summary"]["invalid_files"] += 1

        results["summary"]["total_entries"] += metadata.get("total_entries", 0)
        results["summary"]["valid_entries"] += metadata.get("verified_entries", 0)
        results["summary"]["tampered_entries"] += metadata.get("tampered_entries", 0)

        current += timedelta(days=1)

    # Calculate summary percentages
    if results["summary"]["total_files"] > 0:
        results["summary"]["validity_percentage"] = (
            results["summary"]["valid_files"] / results["summary"]["total_files"] * 100
        )
    else:
        results["summary"]["validity_percentage"] = 100.0

    if results["summary"]["total_entries"] > 0:
        results["summary"]["integrity_percentage"] = (
            (results["summary"]["valid_entries"] - results["summary"]["tampered_entries"]) /
            results["summary"]["total_entries"] * 100
        )
    else:
        results["summary"]["integrity_percentage"] = 100.0

    return results


def generate_integrity_report(output_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Generate a comprehensive integrity report for all audit logs.

    Args:
        output_path: Optional path to save the report file

    Returns:
        Integrity report dictionary
    """
    import os
    from datetime import datetime, timedelta

    # Find the most recent audit logs
    log_dir = Path("Logs/Audit_Trail")

    # Get recent log files
    recent_files = []
    for i in range(7):  # Check last 7 days
        date_str = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        log_file = log_dir / f"gold_audit_{date_str}.jsonl"
        if log_file.exists():
            recent_files.append(log_file)

    report = {
        "report_date": datetime.now().isoformat(),
        "generated_by": "Gold Tier Audit Integrity Verifier",
        "log_directory": str(log_dir),
        "files_scanned": len(recent_files),
        "file_integrity_results": {},
        "overall_status": "UNKNOWN",
        "summary_statistics": {
            "total_files": 0,
            "valid_files": 0,
            "invalid_files": 0,
            "total_entries": 0,
            "valid_entries": 0,
            "tampered_entries": 0
        }
    }

    for file_path in recent_files:
        date_str = file_path.stem.split("_")[-1]  # Extract date from filename
        is_valid, error_msg, metadata = verify_log_file_integrity(file_path)

        report["file_integrity_results"][date_str] = {
            "file_path": str(file_path),
            "is_valid": is_valid,
            "error": error_msg,
            "metadata": metadata
        }

        # Update summary
        report["summary_statistics"]["total_files"] += 1
        if is_valid:
            report["summary_statistics"]["valid_files"] += 1
        else:
            report["summary_statistics"]["invalid_files"] += 1

        report["summary_statistics"]["total_entries"] += metadata.get("total_entries", 0)
        report["summary_statistics"]["valid_entries"] += metadata.get("verified_entries", 0)
        report["summary_statistics"]["tampered_entries"] += metadata.get("tampered_entries", 0)

    # Determine overall status
    if report["summary_statistics"]["invalid_files"] > 0:
        report["overall_status"] = "COMPROMISED"
    elif report["summary_statistics"]["tampered_entries"] > 0:
        report["overall_status"] = "DEGRADED"
    elif report["summary_statistics"]["valid_files"] == report["summary_statistics"]["total_files"]:
        report["overall_status"] = "HEALTHY"
    else:
        report["overall_status"] = "UNKNOWN"

    # Save report if output path is specified
    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)

    return report


def detect_tampering_evidence(log_file_path: Path) -> List[Dict[str, Any]]:
    """
    Detect specific evidence of tampering in audit logs.

    Args:
        log_file_path: Path to the audit log file to analyze

    Returns:
        List of tampering evidence with details
    """
    if not log_file_path.exists():
        return []

    tampering_evidence = []
    entries = []

    # Load entries
    with open(log_file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entry = GoldAuditEntry.from_json(line)
                    entries.append(entry)
                except:
                    tampering_evidence.append({
                        "type": "corrupted_entry",
                        "description": "Could not parse entry from JSON line",
                        "severity": "high"
                    })

    # Check for individual entry tampering
    for i, entry in enumerate(entries):
        if not entry.verify_hash():
            tampering_evidence.append({
                "type": "entry_hash_mismatch",
                "entry_id": entry.entry_id,
                "description": f"Entry {entry.entry_id} hash doesn't match content",
                "severity": "high",
                "index": i
            })

    # Check for chain integrity violations
    if len(entries) > 1:
        for i in range(1, len(entries)):
            current = entries[i]
            previous = entries[i-1]

            if current.previous_entry_hash != previous.entry_hash:
                tampering_evidence.append({
                    "type": "chain_break",
                    "entry_id": current.entry_id,
                    "description": f"Chain broken between entries {previous.entry_id} and {current.entry_id}",
                    "severity": "high",
                    "previous_hash": previous.entry_hash,
                    "expected_hash": current.previous_entry_hash
                })

    # Check for chronological inconsistencies
    for i in range(1, len(entries)):
        prev_time = datetime.fromisoformat(entries[i-1].timestamp.replace('Z', '+00:00'))
        curr_time = datetime.fromisoformat(entries[i].timestamp.replace('Z', '+00:00'))

        if prev_time > curr_time:
            tampering_evidence.append({
                "type": "chronological_inconsistency",
                "description": f"Entry {entries[i].entry_id} has timestamp before previous entry",
                "severity": "medium",
                "previous_timestamp": entries[i-1].timestamp,
                "current_timestamp": entries[i].timestamp
            })

    return tampering_evidence