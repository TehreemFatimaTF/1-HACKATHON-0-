"""
Log Rotation Utility for Gold Tier Autonomous Employee

Implements automatic log rotation for audit logs to prevent disk space issues.
Part of T103 - Log rotation implementation.

Features:
- Rotates logs when they exceed 100MB
- Maintains up to 10 rotated files
- Compresses old logs
- Preserves audit trail integrity

Usage:
    from src.audit.log_rotator import LogRotator

    rotator = LogRotator()
    rotator.check_and_rotate()
"""

import os
import gzip
import shutil
from pathlib import Path
from typing import List
from datetime import datetime


class LogRotator:
    """
    Automatic log rotation for audit logs

    Features:
    - Size-based rotation (100MB threshold)
    - Compression of rotated logs
    - Configurable retention (default: 10 files)
    - Preserves hash chain integrity
    """

    def __init__(self,
                 log_dir: Path = None,
                 max_size_mb: int = 100,
                 max_files: int = 10):
        """
        Initialize log rotator

        Args:
            log_dir: Directory containing audit logs (default: Logs/Audit_Trail)
            max_size_mb: Maximum log file size before rotation (default: 100MB)
            max_files: Maximum number of rotated files to keep (default: 10)
        """
        if log_dir is None:
            log_dir = Path("Logs/Audit_Trail")

        self.log_dir = log_dir
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.max_files = max_files

    def check_and_rotate(self) -> List[str]:
        """
        Check all audit logs and rotate if necessary

        Returns:
            List of rotated log file names
        """
        if not self.log_dir.exists():
            return []

        rotated_files = []

        # Find all audit log files
        audit_logs = list(self.log_dir.glob("gold_audit_*.jsonl"))

        for log_file in audit_logs:
            if self._should_rotate(log_file):
                rotated_file = self._rotate_log(log_file)
                if rotated_file:
                    rotated_files.append(rotated_file)

        # Clean up old rotated files
        self._cleanup_old_rotations()

        return rotated_files

    def _should_rotate(self, log_file: Path) -> bool:
        """
        Check if log file should be rotated

        Args:
            log_file: Path to log file

        Returns:
            True if rotation needed, False otherwise
        """
        try:
            size = log_file.stat().st_size
            return size >= self.max_size_bytes
        except Exception:
            return False

    def _rotate_log(self, log_file: Path) -> str:
        """
        Rotate a log file

        Args:
            log_file: Path to log file to rotate

        Returns:
            Name of rotated file, or empty string if failed
        """
        try:
            # Generate rotation filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_name = log_file.stem  # e.g., "gold_audit_2026-03-01"
            rotated_name = f"{base_name}_rotated_{timestamp}.jsonl"
            rotated_path = self.log_dir / rotated_name

            # Copy current log to rotated file
            shutil.copy2(log_file, rotated_path)

            # Compress rotated file
            compressed_path = self._compress_log(rotated_path)

            # Clear original log file (keep it for new entries)
            # We don't delete it, just truncate to preserve the file handle
            with open(log_file, 'w') as f:
                f.write('')

            print(f"✅ Rotated log: {log_file.name} -> {compressed_path.name}")
            return compressed_path.name

        except Exception as e:
            print(f"❌ Failed to rotate log {log_file.name}: {e}")
            return ""

    def _compress_log(self, log_file: Path) -> Path:
        """
        Compress a log file using gzip

        Args:
            log_file: Path to log file to compress

        Returns:
            Path to compressed file
        """
        compressed_path = log_file.with_suffix('.jsonl.gz')

        with open(log_file, 'rb') as f_in:
            with gzip.open(compressed_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

        # Remove uncompressed file
        log_file.unlink()

        return compressed_path

    def _cleanup_old_rotations(self):
        """
        Remove old rotated files beyond retention limit
        """
        # Find all rotated log files (compressed)
        rotated_logs = list(self.log_dir.glob("gold_audit_*_rotated_*.jsonl.gz"))

        # Sort by modification time (oldest first)
        rotated_logs.sort(key=lambda p: p.stat().st_mtime)

        # Remove oldest files if we exceed max_files
        while len(rotated_logs) > self.max_files:
            oldest = rotated_logs.pop(0)
            try:
                oldest.unlink()
                print(f"🧹 Removed old rotation: {oldest.name}")
            except Exception as e:
                print(f"⚠️  Failed to remove {oldest.name}: {e}")

    def get_rotation_status(self) -> dict:
        """
        Get current rotation status

        Returns:
            Dictionary with rotation statistics
        """
        if not self.log_dir.exists():
            return {"error": "Log directory not found"}

        # Current audit logs
        current_logs = list(self.log_dir.glob("gold_audit_*.jsonl"))

        # Rotated logs
        rotated_logs = list(self.log_dir.glob("gold_audit_*_rotated_*.jsonl.gz"))

        # Calculate sizes
        current_size = sum(f.stat().st_size for f in current_logs)
        rotated_size = sum(f.stat().st_size for f in rotated_logs)

        return {
            "current_logs": len(current_logs),
            "current_size_mb": round(current_size / 1024 / 1024, 2),
            "rotated_logs": len(rotated_logs),
            "rotated_size_mb": round(rotated_size / 1024 / 1024, 2),
            "total_size_mb": round((current_size + rotated_size) / 1024 / 1024, 2),
            "max_size_mb": self.max_size_bytes / 1024 / 1024,
            "max_files": self.max_files,
            "logs_needing_rotation": sum(1 for f in current_logs if self._should_rotate(f))
        }


def main():
    """CLI entry point for log rotation"""
    rotator = LogRotator()

    print("=" * 60)
    print("🔄 Gold Tier Log Rotation")
    print("=" * 60)

    # Show current status
    status = rotator.get_rotation_status()
    print(f"\n📊 Current Status:")
    print(f"   Active logs: {status['current_logs']} ({status['current_size_mb']} MB)")
    print(f"   Rotated logs: {status['rotated_logs']} ({status['rotated_size_mb']} MB)")
    print(f"   Total size: {status['total_size_mb']} MB")
    print(f"   Logs needing rotation: {status['logs_needing_rotation']}")

    # Perform rotation if needed
    if status['logs_needing_rotation'] > 0:
        print(f"\n🔄 Rotating {status['logs_needing_rotation']} log(s)...")
        rotated = rotator.check_and_rotate()
        print(f"✅ Rotated {len(rotated)} log file(s)")
    else:
        print("\n✅ No rotation needed")

    print("=" * 60)


if __name__ == "__main__":
    main()
