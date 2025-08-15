"""
Retry utilities for handling transient failures in database operations.
"""

import random
import time
from functools import wraps
from typing import Any, Callable, Tuple, Type

from sqlalchemy.exc import DisconnectionError, OperationalError, StatementError
from sqlalchemy.exc import TimeoutError as SQLTimeoutError

from app.logger import logger

# Default retryable exceptions for database operations
RETRYABLE_DB_EXCEPTIONS = (
    OperationalError,  # Database connection issues
    DisconnectionError,  # Connection lost during operation
    SQLTimeoutError,  # Query timeout
    StatementError,  # Statement execution issues (some cases)
)


def with_retry(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    retryable_exceptions: Tuple[Type[Exception], ...] = RETRYABLE_DB_EXCEPTIONS,
) -> Callable:
    """
    Decorator that adds retry logic with exponential backoff to functions.

    Args:
        max_retries: Maximum number of retry attempts (default: 3)
        base_delay: Initial delay between retries in seconds (default: 1.0)
        max_delay: Maximum delay between retries in seconds (default: 60.0)
        exponential_base: Base for exponential backoff (default: 2.0)
        jitter: Add random jitter to delay (default: True)
        retryable_exceptions: Tuple of exceptions that should trigger retry
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None

            for attempt in range(max_retries + 1):  # +1 to include initial attempt
                try:
                    return func(*args, **kwargs)
                except retryable_exceptions as e:
                    last_exception = e

                    # Don't retry on the last attempt
                    if attempt == max_retries:
                        logger.error(
                            f"Function {func.__name__} failed after {max_retries + 1} attempts. "
                            f"Final error: {e}"
                        )
                        raise

                    # Calculate delay with exponential backoff
                    delay = min(base_delay * (exponential_base**attempt), max_delay)

                    # Add jitter to prevent thundering herd
                    if jitter:
                        delay = delay * (0.5 + random.random() * 0.5)

                    logger.warning(
                        f"Function {func.__name__} failed on attempt {attempt + 1}/{max_retries + 1}. "
                        f"Error: {e}. Retrying in {delay:.2f} seconds..."
                    )

                    time.sleep(delay)
                except Exception as e:
                    # Non-retryable exception
                    logger.error(
                        f"Function {func.__name__} failed with non-retryable error: {e}"
                    )
                    raise

            # This should never be reached, but just in case
            raise last_exception

        return wrapper

    return decorator


def retry_database_operation(
    operation: Callable, *args, max_retries: int = 3, base_delay: float = 1.0, **kwargs
) -> Any:
    """
    Retry a database operation with exponential backoff.

    This is a functional approach for one-off operations where you don't want
    to use the decorator.

    Args:
        operation: The function to retry
        *args: Positional arguments for the operation
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay between retries in seconds
        **kwargs: Keyword arguments for the operation

    Returns:
        The result of the operation

    Raises:
        The last exception if all retries fail
    """
    last_exception = None

    for attempt in range(max_retries + 1):
        try:
            return operation(*args, **kwargs)
        except RETRYABLE_DB_EXCEPTIONS as e:
            last_exception = e

            if attempt == max_retries:
                logger.error(
                    f"Database operation {operation.__name__} failed after {max_retries + 1} attempts. "
                    f"Final error: {e}"
                )
                raise

            delay = min(base_delay * (2**attempt), 60.0)
            delay = delay * (0.5 + random.random() * 0.5)  # Add jitter

            logger.warning(
                f"Database operation {operation.__name__} failed on attempt {attempt + 1}/{max_retries + 1}. "
                f"Error: {e}. Retrying in {delay:.2f} seconds..."
            )

            time.sleep(delay)
        except Exception as e:
            logger.error(
                f"Database operation {operation.__name__} failed with non-retryable error: {e}"
            )
            raise

    raise last_exception


class RetryableError(Exception):
    """
    Custom exception that can be raised to indicate an operation should be retried.
    """


def is_retryable_error(exception: Exception) -> bool:
    """
    Check if an exception is retryable based on its type and content.

    Args:
        exception: The exception to check

    Returns:
        True if the exception should trigger a retry, False otherwise
    """
    # Check if it's a known retryable exception type
    if isinstance(exception, RETRYABLE_DB_EXCEPTIONS):
        return True

    # Check if it's our custom retryable error
    if isinstance(exception, RetryableError):
        return True

    # Check specific error messages for additional retryable cases
    error_message = str(exception).lower()

    retryable_messages = [
        "connection refused",
        "connection reset",
        "connection timed out",
        "timeout",
        "temporary failure",
        "database is locked",
        "connection lost",
        "server has gone away",
    ]

    return any(message in error_message for message in retryable_messages)


# Specific retry configurations for different types of operations
def retry_db_read(max_retries: int = 3, base_delay: float = 0.5):
    """Retry configuration optimized for read operations."""
    return with_retry(
        max_retries=max_retries,
        base_delay=base_delay,
        max_delay=30.0,
        exponential_base=1.5,
        jitter=True,
    )


def retry_db_write(max_retries: int = 2, base_delay: float = 1.0):
    """Retry configuration optimized for write operations."""
    return with_retry(
        max_retries=max_retries,
        base_delay=base_delay,
        max_delay=45.0,
        exponential_base=2.0,
        jitter=True,
    )


def retry_db_critical(max_retries: int = 5, base_delay: float = 2.0):
    """Retry configuration for critical operations that must succeed."""
    return with_retry(
        max_retries=max_retries,
        base_delay=base_delay,
        max_delay=120.0,
        exponential_base=2.0,
        jitter=True,
    )
