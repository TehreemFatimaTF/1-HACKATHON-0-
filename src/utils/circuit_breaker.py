"""
Circuit Breaker Pattern Implementation
Prevents cascading failures by stopping requests to failing services
"""

import time
import logging
from enum import Enum
from typing import Callable, Any, Optional
from functools import wraps

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "CLOSED"      # Normal operation, requests allowed
    OPEN = "OPEN"          # Failing, requests blocked
    HALF_OPEN = "HALF_OPEN"  # Testing recovery, limited requests


class CircuitBreaker:
    """
    Circuit breaker implementation for protecting against cascading failures.

    States:
    - CLOSED: Normal operation, all requests pass through
    - OPEN: Too many failures, all requests blocked
    - HALF_OPEN: Testing recovery, single request allowed

    Transitions:
    - CLOSED -> OPEN: After failure_threshold consecutive failures
    - OPEN -> HALF_OPEN: After timeout period
    - HALF_OPEN -> CLOSED: If test request succeeds
    - HALF_OPEN -> OPEN: If test request fails
    """

    def __init__(
        self,
        failure_threshold: int = 3,
        timeout: float = 60.0,
        name: str = "CircuitBreaker"
    ):
        """
        Initialize circuit breaker.

        Args:
            failure_threshold: Number of failures before opening circuit
            timeout: Seconds to wait before attempting recovery
            name: Name for logging purposes
        """
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.name = name

        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.opened_at: Optional[float] = None

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection.

        Args:
            func: Function to execute
            *args: Positional arguments for func
            **kwargs: Keyword arguments for func

        Returns:
            Function result

        Raises:
            CircuitBreakerOpen: If circuit is open
            Exception: If function raises exception
        """
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                logger.info(f"{self.name}: Entering HALF_OPEN state")
            else:
                raise CircuitBreakerOpen(
                    f"{self.name}: Circuit breaker is OPEN. "
                    f"Retry in {self._time_until_reset():.0f}s"
                )

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise

    def _on_success(self):
        """Handle successful call"""
        if self.state == CircuitState.HALF_OPEN:
            logger.info(f"{self.name}: Recovery successful, closing circuit")
            self.state = CircuitState.CLOSED

        self.failure_count = 0
        self.last_failure_time = None

    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.state == CircuitState.HALF_OPEN:
            logger.warning(f"{self.name}: Recovery failed, reopening circuit")
            self.state = CircuitState.OPEN
            self.opened_at = time.time()
        elif self.failure_count >= self.failure_threshold:
            logger.error(
                f"{self.name}: Opening circuit after {self.failure_count} failures"
            )
            self.state = CircuitState.OPEN
            self.opened_at = time.time()

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        if self.opened_at is None:
            return False
        return (time.time() - self.opened_at) >= self.timeout

    def _time_until_reset(self) -> float:
        """Calculate time until reset attempt"""
        if self.opened_at is None:
            return 0
        elapsed = time.time() - self.opened_at
        return max(0, self.timeout - elapsed)

    def reset(self):
        """Manually reset circuit breaker to CLOSED state"""
        logger.info(f"{self.name}: Manual reset to CLOSED state")
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None
        self.opened_at = None

    def get_state(self) -> dict:
        """Get current circuit breaker state"""
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "failure_threshold": self.failure_threshold,
            "last_failure_time": self.last_failure_time,
            "opened_at": self.opened_at,
            "timeout": self.timeout
        }


class CircuitBreakerOpen(Exception):
    """Exception raised when circuit breaker is open"""
    pass


def circuit_breaker(
    failure_threshold: int = 3,
    timeout: float = 60.0,
    name: Optional[str] = None
):
    """
    Decorator for applying circuit breaker pattern to functions.

    Args:
        failure_threshold: Number of failures before opening circuit
        timeout: Seconds to wait before attempting recovery
        name: Name for logging (defaults to function name)

    Example:
        @circuit_breaker(failure_threshold=5, timeout=30)
        def call_external_api():
            # API call that might fail
            pass
    """
    def decorator(func: Callable):
        breaker_name = name or func.__name__
        breaker = CircuitBreaker(failure_threshold, timeout, breaker_name)

        @wraps(func)
        def wrapper(*args, **kwargs):
            return breaker.call(func, *args, **kwargs)

        wrapper.circuit_breaker = breaker  # Expose breaker for inspection
        return wrapper

    return decorator
