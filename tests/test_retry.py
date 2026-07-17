"""Test retry mechanism functionality."""

import pytest
import time
from unittest.mock import Mock, patch

from cli_agent.utils.retry import retry_with_backoff, RetryContext
from cli_agent.utils.exceptions import RetryError


class TestRetryWithBackoff:
    """Test the retry_with_backoff decorator."""

    def test_successful_first_attempt(self):
        """Test function that succeeds on first attempt."""
        call_count = 0

        @retry_with_backoff(max_retries=3, base_delay=0.01)
        def success_func():
            nonlocal call_count
            call_count += 1
            return "success"

        result = success_func()
        assert result == "success"
        assert call_count == 1

    def test_successful_after_retries(self):
        """Test function that succeeds after some failures."""
        call_count = 0

        @retry_with_backoff(max_retries=3, base_delay=0.01)
        def flaky_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError(f"Attempt {call_count} failed")
            return "success"

        result = flaky_func()
        assert result == "success"
        assert call_count == 3

    def test_exhausts_all_retries(self):
        """Test function that fails all attempts."""
        call_count = 0

        @retry_with_backoff(max_retries=3, base_delay=0.01)
        def always_fail():
            nonlocal call_count
            call_count += 1
            raise ValueError("Always fails")

        with pytest.raises(RetryError) as exc_info:
            always_fail()

        assert call_count == 4  # Initial + 3 retries
        assert "failed after 3 retries" in str(exc_info.value)

    def test_retryable_exceptions_only(self):
        """Test that only specified exceptions trigger retries."""
        call_count = 0

        @retry_with_backoff(
            max_retries=3,
            base_delay=0.01,
            retryable_exceptions=(ValueError,)
        )
        def selective_fail():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise ValueError("Retryable")
            raise TypeError("Not retryable")

        with pytest.raises(TypeError):
            selective_fail()

        assert call_count == 2  # First attempt + one retry before TypeError

    def test_exponential_backoff_timing(self):
        """Test that delays increase exponentially."""
        call_times = []

        @retry_with_backoff(max_retries=3, base_delay=0.1, jitter=False)
        def track_timing():
            call_times.append(time.time())
            raise ValueError("Fail")

        with pytest.raises(RetryError):
            track_timing()

        # Check that delays are increasing
        if len(call_times) >= 3:
            delay1 = call_times[1] - call_times[0]
            delay2 = call_times[2] - call_times[1]
            assert delay2 > delay1  # Exponential increase


class TestRetryContext:
    """Test the RetryContext class."""

    def test_successful_execution(self):
        """Test successful function execution."""
        with RetryContext(max_retries=3, operation_name="test") as ctx:
            result = ctx.execute(lambda: "success")
            assert result == "success"
            assert ctx.attempts == 1

    def test_retry_then_success(self):
        """Test retry logic with eventual success."""
        call_count = 0

        def flaky():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("Fail")
            return "success"

        with RetryContext(max_retries=3, base_delay=0.01, operation_name="test") as ctx:
            result = ctx.execute(flaky)
            assert result == "success"
            assert ctx.attempts == 2

    def test_exhausts_retries(self):
        """Test that RetryError is raised after exhausting retries."""
        def always_fail():
            raise ValueError("Always fails")

        with pytest.raises(RetryError):
            with RetryContext(max_retries=2, base_delay=0.01, operation_name="test") as ctx:
                ctx.execute(always_fail)

    def test_tracks_last_error(self):
        """Test that last error is tracked."""
        def fail_with_specific_error():
            raise RuntimeError("Specific error")

        with pytest.raises(RetryError):
            with RetryContext(max_retries=1, base_delay=0.01, operation_name="test") as ctx:
                ctx.execute(fail_with_specific_error)
                assert isinstance(ctx.last_error, RuntimeError)
                assert "Specific error" in str(ctx.last_error)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
