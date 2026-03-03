"""
Security Utilities for Gold Tier Autonomous Employee

Provides input validation, output sanitization, and security hardening.
Part of T101 - Security hardening implementation.

Usage:
    from src.utils.security import SecurityValidator

    validator = SecurityValidator()
    safe_input = validator.sanitize_input(user_input)
    validator.validate_email(email)
"""

import re
import html
from typing import Any, Dict, Optional
from pathlib import Path
import json


class SecurityValidator:
    """
    Security validation and sanitization utilities

    Features:
    - Input validation (email, URL, file paths)
    - Output sanitization (prevent XSS, injection)
    - File path validation (prevent directory traversal)
    - API key validation
    - SQL injection prevention
    """

    # Regex patterns for validation
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    URL_PATTERN = re.compile(r'^https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(/.*)?$')
    SAFE_FILENAME_PATTERN = re.compile(r'^[a-zA-Z0-9._-]+$')

    # Dangerous patterns to block
    SQL_INJECTION_PATTERNS = [
        r"(\bUNION\b.*\bSELECT\b)",
        r"(\bDROP\b.*\bTABLE\b)",
        r"(\bINSERT\b.*\bINTO\b)",
        r"(\bDELETE\b.*\bFROM\b)",
        r"(--)",
        r"(;.*--)",
        r"(\bOR\b.*=.*)",
    ]

    COMMAND_INJECTION_PATTERNS = [
        r"(&&)",
        r"(\|\|)",
        r"(;)",
        r"(`)",
        r"(\$\()",
        r"(\beval\b)",
        r"(\bexec\b)",
    ]

    def __init__(self):
        """Initialize security validator"""
        self.blocked_attempts = []

    def validate_email(self, email: str) -> bool:
        """
        Validate email address format

        Args:
            email: Email address to validate

        Returns:
            True if valid, False otherwise
        """
        if not email or not isinstance(email, str):
            return False

        return bool(self.EMAIL_PATTERN.match(email))

    def validate_url(self, url: str, allowed_schemes: Optional[list] = None) -> bool:
        """
        Validate URL format and scheme

        Args:
            url: URL to validate
            allowed_schemes: List of allowed schemes (default: ['http', 'https'])

        Returns:
            True if valid, False otherwise
        """
        if not url or not isinstance(url, str):
            return False

        if allowed_schemes is None:
            allowed_schemes = ['http', 'https']

        # Check basic URL format
        if not self.URL_PATTERN.match(url):
            return False

        # Check scheme
        scheme = url.split('://')[0].lower()
        return scheme in allowed_schemes

    def validate_file_path(self, file_path: str, base_dir: Optional[Path] = None) -> bool:
        """
        Validate file path to prevent directory traversal attacks

        Args:
            file_path: File path to validate
            base_dir: Base directory to restrict access (optional)

        Returns:
            True if valid, False otherwise
        """
        if not file_path or not isinstance(file_path, str):
            return False

        # Check for directory traversal patterns
        if '..' in file_path or file_path.startswith('/'):
            self._log_security_event("Directory traversal attempt", file_path)
            return False

        # If base_dir specified, ensure path is within it
        if base_dir:
            try:
                full_path = (base_dir / file_path).resolve()
                base_path = base_dir.resolve()
                if not str(full_path).startswith(str(base_path)):
                    self._log_security_event("Path escape attempt", file_path)
                    return False
            except Exception:
                return False

        return True

    def sanitize_input(self, user_input: str, max_length: int = 10000) -> str:
        """
        Sanitize user input to prevent injection attacks

        Args:
            user_input: Raw user input
            max_length: Maximum allowed length

        Returns:
            Sanitized input string
        """
        if not user_input or not isinstance(user_input, str):
            return ""

        # Truncate to max length
        sanitized = user_input[:max_length]

        # Remove null bytes
        sanitized = sanitized.replace('\x00', '')

        # HTML escape to prevent XSS
        sanitized = html.escape(sanitized)

        return sanitized

    def sanitize_output(self, output: str) -> str:
        """
        Sanitize output before displaying to user

        Args:
            output: Raw output string

        Returns:
            Sanitized output string
        """
        if not output or not isinstance(output, str):
            return ""

        # HTML escape
        sanitized = html.escape(output)

        return sanitized

    def check_sql_injection(self, query: str) -> bool:
        """
        Check for SQL injection patterns

        Args:
            query: SQL query or user input to check

        Returns:
            True if safe, False if injection detected
        """
        if not query or not isinstance(query, str):
            return True

        query_upper = query.upper()

        for pattern in self.SQL_INJECTION_PATTERNS:
            if re.search(pattern, query_upper, re.IGNORECASE):
                self._log_security_event("SQL injection attempt", query)
                return False

        return True

    def check_command_injection(self, command: str) -> bool:
        """
        Check for command injection patterns

        Args:
            command: Command or user input to check

        Returns:
            True if safe, False if injection detected
        """
        if not command or not isinstance(command, str):
            return True

        for pattern in self.COMMAND_INJECTION_PATTERNS:
            if re.search(pattern, command):
                self._log_security_event("Command injection attempt", command)
                return False

        return True

    def validate_api_key(self, api_key: str, min_length: int = 20) -> bool:
        """
        Validate API key format

        Args:
            api_key: API key to validate
            min_length: Minimum required length

        Returns:
            True if valid, False otherwise
        """
        if not api_key or not isinstance(api_key, str):
            return False

        # Check length
        if len(api_key) < min_length:
            return False

        # Check for placeholder values
        if api_key.startswith('your_') or api_key == 'placeholder':
            return False

        return True

    def sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename to prevent path traversal and injection

        Args:
            filename: Original filename

        Returns:
            Sanitized filename
        """
        if not filename or not isinstance(filename, str):
            return "unnamed_file"

        # Remove path components
        filename = Path(filename).name

        # Remove dangerous characters
        filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)

        # Limit length
        if len(filename) > 255:
            filename = filename[:255]

        return filename

    def validate_json(self, json_str: str, max_size: int = 1048576) -> bool:
        """
        Validate JSON string safely

        Args:
            json_str: JSON string to validate
            max_size: Maximum allowed size in bytes (default: 1MB)

        Returns:
            True if valid, False otherwise
        """
        if not json_str or not isinstance(json_str, str):
            return False

        # Check size
        if len(json_str.encode('utf-8')) > max_size:
            self._log_security_event("JSON size exceeded", f"{len(json_str)} bytes")
            return False

        # Try parsing
        try:
            json.loads(json_str)
            return True
        except json.JSONDecodeError:
            return False

    def _log_security_event(self, event_type: str, details: str):
        """Log security event for audit"""
        event = {
            "type": event_type,
            "details": details[:200],  # Truncate for safety
            "timestamp": str(Path(__file__).stat().st_mtime)
        }
        self.blocked_attempts.append(event)

        # Log to file
        log_file = Path("Logs/security_events.json")
        try:
            if log_file.exists():
                with open(log_file, 'r') as f:
                    events = json.load(f)
            else:
                events = {"events": []}

            events["events"].append(event)

            # Keep only last 1000 events
            if len(events["events"]) > 1000:
                events["events"] = events["events"][-1000:]

            log_file.parent.mkdir(parents=True, exist_ok=True)
            with open(log_file, 'w') as f:
                json.dump(events, f, indent=2)

        except Exception as e:
            print(f"Warning: Failed to log security event: {e}")


# Global instance
_global_validator = None


def get_validator() -> SecurityValidator:
    """Get global security validator instance"""
    global _global_validator
    if _global_validator is None:
        _global_validator = SecurityValidator()
    return _global_validator
