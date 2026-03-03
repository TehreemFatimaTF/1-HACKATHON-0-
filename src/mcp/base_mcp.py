"""
Base MCP (Model Context Protocol) Client
Provides common functionality for all MCP server integrations with health checks,
retry logic, and circuit breaker pattern.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from enum import Enum
import time
import logging

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """MCP server health status"""
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    FAILED = "FAILED"
    RECOVERING = "RECOVERING"
    UNKNOWN = "UNKNOWN"


class CircuitBreakerState(Enum):
    """Circuit breaker states"""
    CLOSED = "CLOSED"  # Normal operation
    OPEN = "OPEN"      # Failing, reject requests
    HALF_OPEN = "HALF_OPEN"  # Testing recovery


class BaseMCPClient(ABC):
    """
    Abstract base class for all MCP server clients.
    Provides health checking, retry logic, and circuit breaker functionality.
    """

    def __init__(self, server_name: str, endpoint_url: str):
        self.server_name = server_name
        self.endpoint_url = endpoint_url

        # Health tracking
        self.health_status = HealthStatus.UNKNOWN
        self.last_success: Optional[float] = None
        self.last_failure: Optional[float] = None
        self.consecutive_failures = 0

        # Statistics
        self.total_calls = 0
        self.successful_calls = 0
        self.failed_calls = 0

        # Circuit breaker
        self.circuit_breaker_state = CircuitBreakerState.CLOSED
        self.circuit_breaker_opened_at: Optional[float] = None
        self.circuit_breaker_timeout = 60  # seconds
        self.failure_threshold = 3

        # Performance tracking
        self.response_times = []
        self.max_response_times = 100  # Keep last 100 response times

    @abstractmethod
    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on the MCP server.
        Must be implemented by subclasses.

        Returns:
            Dict with health status information
        """
        pass

    @abstractmethod
    def _make_request(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make actual API request to MCP server.
        Must be implemented by subclasses.

        Args:
            endpoint: API endpoint path
            data: Request payload

        Returns:
            Response data
        """
        pass

    def call(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make API call with circuit breaker protection.

        Args:
            endpoint: API endpoint path
            data: Request payload

        Returns:
            Response data

        Raises:
            CircuitBreakerOpen: If circuit breaker is open
            Exception: If request fails
        """
        # Check circuit breaker
        if self.circuit_breaker_state == CircuitBreakerState.OPEN:
            if self._should_attempt_reset():
                self.circuit_breaker_state = CircuitBreakerState.HALF_OPEN
                logger.info(f"{self.server_name}: Circuit breaker entering HALF_OPEN state")
            else:
                raise CircuitBreakerOpen(
                    f"{self.server_name}: Circuit breaker is OPEN. "
                    f"Retry after {self._time_until_reset():.0f} seconds"
                )

        # Make request
        start_time = time.time()
        self.total_calls += 1

        try:
            response = self._make_request(endpoint, data)
            response_time = (time.time() - start_time) * 1000  # ms

            self._record_success(response_time)
            return response

        except Exception as e:
            self._record_failure()
            raise

    def _record_success(self, response_time: float):
        """Record successful API call"""
        self.successful_calls += 1
        self.last_success = time.time()
        self.consecutive_failures = 0

        # Track response time
        self.response_times.append(response_time)
        if len(self.response_times) > self.max_response_times:
            self.response_times.pop(0)

        # Update health status
        if self.circuit_breaker_state == CircuitBreakerState.HALF_OPEN:
            self.circuit_breaker_state = CircuitBreakerState.CLOSED
            logger.info(f"{self.server_name}: Circuit breaker CLOSED (recovered)")

        self.health_status = HealthStatus.HEALTHY

    def _record_failure(self):
        """Record failed API call"""
        self.failed_calls += 1
        self.last_failure = time.time()
        self.consecutive_failures += 1

        # Check if we should open circuit breaker
        if self.consecutive_failures >= self.failure_threshold:
            if self.circuit_breaker_state != CircuitBreakerState.OPEN:
                self.circuit_breaker_state = CircuitBreakerState.OPEN
                self.circuit_breaker_opened_at = time.time()
                logger.error(
                    f"{self.server_name}: Circuit breaker OPENED after "
                    f"{self.consecutive_failures} consecutive failures"
                )
            self.health_status = HealthStatus.FAILED
        else:
            self.health_status = HealthStatus.DEGRADED

    def _should_attempt_reset(self) -> bool:
        """Check if circuit breaker should attempt reset"""
        if self.circuit_breaker_opened_at is None:
            return False

        elapsed = time.time() - self.circuit_breaker_opened_at
        return elapsed >= self.circuit_breaker_timeout

    def _time_until_reset(self) -> float:
        """Calculate time until circuit breaker reset attempt"""
        if self.circuit_breaker_opened_at is None:
            return 0

        elapsed = time.time() - self.circuit_breaker_opened_at
        return max(0, self.circuit_breaker_timeout - elapsed)

    def get_success_rate(self) -> float:
        """Calculate success rate"""
        if self.total_calls == 0:
            return 0.0
        return self.successful_calls / self.total_calls

    def get_average_response_time(self) -> float:
        """Calculate average response time in milliseconds"""
        if not self.response_times:
            return 0.0
        return sum(self.response_times) / len(self.response_times)

    def get_status(self) -> Dict[str, Any]:
        """Get current client status"""
        return {
            "server_name": self.server_name,
            "health_status": self.health_status.value,
            "circuit_breaker_state": self.circuit_breaker_state.value,
            "last_success": self.last_success,
            "last_failure": self.last_failure,
            "consecutive_failures": self.consecutive_failures,
            "total_calls": self.total_calls,
            "successful_calls": self.successful_calls,
            "failed_calls": self.failed_calls,
            "success_rate": self.get_success_rate(),
            "average_response_time_ms": self.get_average_response_time()
        }


class CircuitBreakerOpen(Exception):
    """Exception raised when circuit breaker is open"""
    pass
