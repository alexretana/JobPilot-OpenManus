"""
Test retry mechanisms for database operations.
"""

from unittest.mock import patch

import pytest
from sqlalchemy.exc import DisconnectionError, OperationalError

from app.utils.retry import (
    RetryableError,
    is_retryable_error,
    retry_database_operation,
    with_retry,
)


def test_retry_decorator_success():
    """Test retry decorator on successful operation."""
    call_count = 0

    @with_retry(max_retries=3)
    def test_function():
        nonlocal call_count
        call_count += 1
        return "success"

    result = test_function()
    assert result == "success"
    assert call_count == 1


def test_retry_decorator_with_transient_failure():
    """Test retry decorator with transient failure then success."""
    call_count = 0

    @with_retry(max_retries=3, base_delay=0.01)  # Fast retry for testing
    def test_function():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise OperationalError("connection failed", "", "")
        return "success"

    result = test_function()
    assert result == "success"
    assert call_count == 3


def test_retry_decorator_max_retries_exceeded():
    """Test retry decorator when max retries are exceeded."""
    call_count = 0

    @with_retry(max_retries=2, base_delay=0.01)  # Fast retry for testing
    def test_function():
        nonlocal call_count
        call_count += 1
        raise OperationalError("persistent failure", "", "")

    with pytest.raises(OperationalError):
        test_function()

    assert call_count == 3  # Initial call + 2 retries


def test_retry_decorator_non_retryable_exception():
    """Test retry decorator with non-retryable exception."""
    call_count = 0

    @with_retry(max_retries=3, base_delay=0.01)
    def test_function():
        nonlocal call_count
        call_count += 1
        raise ValueError("non-retryable error")

    with pytest.raises(ValueError):
        test_function()

    assert call_count == 1  # Should not retry


def test_retry_database_operation_function():
    """Test the functional retry approach."""
    call_count = 0

    def failing_operation():
        nonlocal call_count
        call_count += 1
        if call_count < 2:
            raise DisconnectionError("connection lost", "", "")
        return "operation_result"

    result = retry_database_operation(failing_operation, max_retries=3, base_delay=0.01)
    assert result == "operation_result"
    assert call_count == 2


def test_is_retryable_error():
    """Test the retryable error detection logic."""
    # Known retryable exceptions
    assert is_retryable_error(OperationalError("db error", "", ""))
    assert is_retryable_error(DisconnectionError("disconnected", "", ""))
    assert is_retryable_error(RetryableError("custom retryable"))

    # Non-retryable exceptions
    assert not is_retryable_error(ValueError("validation error"))
    assert not is_retryable_error(KeyError("missing key"))

    # Message-based detection
    assert is_retryable_error(Exception("connection refused"))
    assert is_retryable_error(Exception("timeout occurred"))
    assert is_retryable_error(Exception("database is locked"))
    assert not is_retryable_error(Exception("invalid syntax"))


def test_retry_with_jitter():
    """Test that jitter is applied to delays."""
    call_count = 0
    delays = []

    # Patch time.sleep to capture delays
    def mock_sleep(duration):
        delays.append(duration)

    @with_retry(max_retries=3, base_delay=1.0, jitter=True)
    def test_function():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise OperationalError("error", "", "")
        return "success"

    with patch("app.utils.retry.time.sleep", side_effect=mock_sleep):
        result = test_function()

    assert result == "success"
    assert call_count == 3
    assert len(delays) == 2  # Two retry delays

    # Delays should be different due to jitter (very unlikely to be exactly the same)
    assert delays[0] != delays[1]

    # Delays should be within reasonable bounds (base_delay * 0.5 to base_delay * exponential_factor)
    for delay in delays:
        assert (
            0.5 <= delay <= 10.0
        )  # Should be reasonable for exponential backoff with jitter


@patch("app.utils.retry.logger")
def test_retry_logging(mock_logger):
    """Test that retry attempts are properly logged."""
    call_count = 0

    @with_retry(max_retries=2, base_delay=0.01)
    def test_function():
        nonlocal call_count
        call_count += 1
        if call_count < 2:
            raise OperationalError("test error", "", "")
        return "success"

    result = test_function()
    assert result == "success"

    # Check that warning was logged for retry attempt
    mock_logger.warning.assert_called()
    warning_calls = mock_logger.warning.call_args_list
    assert len(warning_calls) == 1

    warning_message = warning_calls[0][0][0]  # First call, first argument
    assert "failed on attempt" in warning_message
    assert "Retrying in" in warning_message


def test_retry_with_custom_exceptions():
    """Test retry with custom retryable exceptions."""
    call_count = 0

    class CustomError(Exception):
        pass

    @with_retry(max_retries=2, base_delay=0.01, retryable_exceptions=(CustomError,))
    def test_function():
        nonlocal call_count
        call_count += 1
        if call_count < 2:
            raise CustomError("custom error")
        return "success"

    result = test_function()
    assert result == "success"
    assert call_count == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
