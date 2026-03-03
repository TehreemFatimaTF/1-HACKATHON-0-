"""
Retry decorator with exponential backoff
Provides configurable retry logic for transient failures
"""

import time
import logging
from functools import wraps
from typing import Callable, Type, Tuple
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)

logger = logging.getLogger(__name__)


def retry_with_backoff(
    max_attempts: int = 5,
    min_wait: float = 1.0,
    max_wait: float = 16.0,
    multiplier: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
):
    """
    Decorator for retrying functions with exponential backoff.

    Args:
        max_attempts: Maximum number of retry attempts
        min_wait: Minimum wait time in seconds
        max_wait: Maximum wait time in seconds
        multiplier: Exponential backoff multiplier
        exceptions: Tuple of exception types to retry on

    Example:
        @retry_with_backoff(max_attempts=3, min_wait=1, max_wait=10)
        def call_api():
            # API call that might fail
            pass
    """
    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(
            multiplier=multiplier,
            min=min_wait,
            max=max_wait
        ),
        retry=retry_if_exception_type(exceptions),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True
    )


def simple_retry(max_attempts: int = 3, delay: float = 1.0):
    """
    Simple retry decorator with fixed delay.

    Args:
        max_attempts: Maximum number of retry attempts
        delay: Fixed delay between retries in seconds

    Example:
        @simple_retry(max_attempts=3, delay=2.0)
        def flaky_operation():
            # Operation that might fail
            pass
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_attempts} failed for {func.__name__}: {e}. "
                            f"Retrying in {delay}s..."
                        )
                        time.sleep(delay)
                    else:
                        logger.error(
                            f"All {max_attempts} attempts failed for {func.__name__}: {e}"
                        )

            raise last_exception

        return wrapper
    return decorator
