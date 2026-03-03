"""
MCPServerConnection model with health tracking for the Gold Tier system.
Test ID: T084 [P] [US4] Create MCPServerConnection model with health tracking
File: src/models/mcp_connection.py
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum


class HealthStatus(Enum):
    """Health status of MCP server connections"""
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    FAILED = "FAILED"
    RECOVERING = "RECOVERING"
    UNKNOWN = "UNKNOWN"


class AuthState(Enum):
    """Authentication state of MCP server connections"""
    AUTHENTICATED = "AUTHENTICATED"
    UNAUTHENTICATED = "UNAUTHENTICATED"
    EXPIRED = "EXPIRED"
    INVALID = "INVALID"


class CircuitBreakerState(Enum):
    """Circuit breaker state for MCP server connections"""
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


@dataclass
class MCPServerConnection:
    """
    Model representing the connection and health status of an MCP server
    """
    server_name: str
    health_status: HealthStatus = field(default=HealthStatus.UNKNOWN)
    auth_state: AuthState = field(default=AuthState.UNAUTHENTICATED)

    # Connection statistics
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    consecutive_failures: int = 0
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    success_rate: float = 0.0
    average_response_time_ms: float = 0.0

    # Circuit breaker tracking
    circuit_breaker_state: CircuitBreakerState = field(default=CircuitBreakerState.CLOSED)
    last_updated: datetime = field(default_factory=datetime.utcnow)

    # Platform-specific rate limit info
    rate_limit_info: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert the connection to a dictionary for JSON serialization."""
        return {
            'server_name': self.server_name,
            'health_status': self.health_status.value,
            'auth_state': self.auth_state.value,
            'last_success': self.last_success.isoformat() + "Z" if self.last_success else None,
            'last_failure': self.last_failure.isoformat() + "Z" if self.last_failure else None,
            'consecutive_failures': self.consecutive_failures,
            'total_calls': self.total_calls,
            'successful_calls': self.successful_calls,
            'failed_calls': self.failed_calls,
            'success_rate': self.success_rate,
            'average_response_time_ms': self.average_response_time_ms,
            'circuit_breaker_state': self.circuit_breaker_state.value,
            'last_updated': self.last_updated.isoformat() + "Z",
            'rate_limit_info': self.rate_limit_info
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MCPServerConnection':
        """Create a connection from a dictionary."""
        from datetime import datetime
        from dateutil.parser import parse

        # Convert string timestamps back to datetime
        last_success = None
        if data.get('last_success'):
            last_success = parse(data['last_success']) if isinstance(data['last_success'], str) else data['last_success']

        last_failure = None
        if data.get('last_failure'):
            last_failure = parse(data['last_failure']) if isinstance(data['last_failure'], str) else data['last_failure']

        last_updated = datetime.utcnow()
        if data.get('last_updated'):
            last_updated = parse(data['last_updated']) if isinstance(data['last_updated'], str) else data['last_updated']

        # Convert string enums back to enum objects
        health_status = HealthStatus(data['health_status']) if data.get('health_status') else HealthStatus.UNKNOWN
        auth_state = AuthState(data['auth_state']) if data.get('auth_state') else AuthState.UNAUTHENTICATED
        circuit_breaker_state = CircuitBreakerState(data['circuit_breaker_state']) if data.get('circuit_breaker_state') else CircuitBreakerState.CLOSED

        return cls(
            server_name=data['server_name'],
            health_status=health_status,
            auth_state=auth_state,
            last_success=last_success,
            last_failure=last_failure,
            consecutive_failures=data.get('consecutive_failures', 0),
            total_calls=data.get('total_calls', 0),
            successful_calls=data.get('successful_calls', 0),
            failed_calls=data.get('failed_calls', 0),
            success_rate=data.get('success_rate', 0.0),
            average_response_time_ms=data.get('average_response_time_ms', 0.0),
            circuit_breaker_state=circuit_breaker_state,
            rate_limit_info=data.get('rate_limit_info', {}),
            last_updated=last_updated
        )

    def get_health_summary(self) -> Dict[str, Any]:
        """Get a summary of the connection health."""
        return {
            'server_name': self.server_name,
            'health_status': self.health_status.value,
            'auth_state': self.auth_state.value,
            'success_rate': self.success_rate,
            'consecutive_failures': self.consecutive_failures,
            'circuit_breaker_state': self.circuit_breaker_state.value,
            'last_updated': self.last_updated.isoformat() + "Z"
        }

    def update_success_metrics(self, response_time_ms: float):
        """Update metrics after a successful call."""
        self.successful_calls += 1
        self.total_calls += 1
        self.last_success = datetime.utcnow()

        # Update success rate
        if self.total_calls > 0:
            self.success_rate = (self.successful_calls / self.total_calls) * 100

        # Update average response time
        all_response_times = [response_time_ms]
        if hasattr(self, '_response_times') and self._response_times:
            all_response_times.extend(self._response_times)

        if all_response_times:
            self.average_response_time_ms = sum(all_response_times) / len(all_response_times)

        self.consecutive_failures = 0

        # Store recent response times for average calculation
        if not hasattr(self, '_response_times'):
            self._response_times = []
        self._response_times.append(response_time_ms)

        # Keep only the last 100 response times to prevent memory issues
        if len(self._response_times) > 100:
            self._response_times = self._response_times[-100:]

    def update_failure_metrics(self):
        """Update metrics after a failed call."""
        self.failed_calls += 1
        self.total_calls += 1
        self.last_failure = datetime.utcnow()
        self.consecutive_failures += 1

        # Update success rate
        if self.total_calls > 0:
            self.success_rate = (self.successful_calls / self.total_calls) * 100