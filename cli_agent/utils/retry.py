"""Retry mechanism with exponential backoff."""

import time
import random
from typing import Callable, Any, Optional, Type
from functools import wraps

from .logger import get_logger
from .exceptions import RetryError

logger = get_logger(__name__)


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    retryable_exceptions: Optional[tuple] = None,
):
    """
    Decorator for retrying functions with exponential backoff and jitter.

    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay between retries in seconds
        max_delay: Maximum delay between retries in seconds
        exponential_base: Base for exponential backoff calculation
        jitter: Whether to add random jitter to prevent thundering herd
        retryable_exceptions: Tuple of exception types that should trigger retry
                            (if None, all exceptions trigger retry)

    Returns:
        Decorated function with retry logic

    Example:
        @retry_with_backoff(max_retries=3, base_delay=1.0)
        def flaky_api_call():
            # ... code that might fail
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    # Check if this exception is retryable
                    if retryable_exceptions and not isinstance(e, retryable_exceptions):
                        raise
                    
                    # If we've exhausted retries, raise RetryError
                    if attempt >= max_retries:
                        logger.error(
                            f"Function '{func.__name__}' failed after {max_retries} retries"
                        )
                        raise RetryError(
                            tool_name=func.__name__,
                            max_retries=max_retries,
                            last_error=last_exception
                        )
                    
                    # Calculate delay with exponential backoff
                    delay = min(
                        base_delay * (exponential_base ** attempt),
                        max_delay
                    )
                    
                    # Add jitter to prevent thundering herd problem
                    if jitter:
                        delay = delay * (0.5 + random.random() * 0.5)
                    
                    logger.warning(
                        f"Attempt {attempt + 1}/{max_retries} failed for '{func.__name__}': {str(e)}. "
                        f"Retrying in {delay:.2f}s..."
                    )
                    
                    time.sleep(delay)
            
            # This should never be reached, but just in case
            raise last_exception
        
        return wrapper
    return decorator


class RetryContext:
    """Context manager for retry logic with state tracking."""

    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        operation_name: str = "operation"
    ):
        """
        Initialize retry context.

        Args:
            max_retries: Maximum number of retries
            base_delay: Base delay between retries
            max_delay: Maximum delay cap
            operation_name: Name of the operation for logging
        """
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.operation_name = operation_name
        self.attempts = 0
        self.last_error = None

    def __enter__(self):
        """Enter context."""
        self.attempts = 0
        self.last_error = None
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context - don't suppress exceptions."""
        return False

    def execute(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with retry logic.

        Args:
            func: Function to execute
            *args: Positional arguments for function
            **kwargs: Keyword arguments for function

        Returns:
            Function result

        Raises:
            RetryError: If all retries are exhausted
        """
        last_exception = None

        for attempt in range(self.max_retries + 1):
            self.attempts = attempt + 1
            try:
                result = func(*args, **kwargs)
                if attempt > 0:
                    logger.info(
                        f"'{self.operation_name}' succeeded on attempt {attempt + 1}"
                    )
                return result
            except Exception as e:
                last_exception = e
                self.last_error = e

                if attempt >= self.max_retries:
                    logger.error(
                        f"'{self.operation_name}' failed after {self.max_retries} retries"
                    )
                    raise RetryError(
                        tool_name=self.operation_name,
                        max_retries=self.max_retries,
                        last_error=last_exception
                    )

                # Calculate delay with exponential backoff and jitter
                delay = min(
                    self.base_delay * (2 ** attempt),
                    self.max_delay
                )
                delay = delay * (0.5 + random.random() * 0.5)  # Add jitter

                logger.warning(
                    f"Attempt {attempt + 1}/{self.max_retries} failed for '{self.operation_name}': {str(e)}. "
                    f"Retrying in {delay:.2f}s..."
                )

                time.sleep(delay)

        raise last_exception
