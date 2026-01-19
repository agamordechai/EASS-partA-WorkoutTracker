"""Tests for the async refresh script (Session 09).

These tests use pytest-anyio for async testing.
Run with: pytest scripts/test_refresh.py -v --anyio-backends=asyncio
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from dataclasses import dataclass

# Import the refresh module
from scripts.refresh import (
    RefreshConfig,
    RefreshResult,
    IdempotencyStore,
    ExerciseRefresher,
)


@pytest.fixture
def config():
    """Default test configuration."""
    return RefreshConfig(
        api_url="http://test:8000",
        redis_url="redis://test:6379/0",
        max_concurrency=2,
        max_retries=2,
        retry_base_delay=0.01,  # Fast retries for tests
        idempotency_ttl=60,
        timeout=5.0
    )


@pytest.fixture
def sample_exercises():
    """Sample exercise data."""
    return [
        {"id": 1, "name": "Bench Press", "sets": 4, "reps": 8, "weight": 80.0},
        {"id": 2, "name": "Squat", "sets": 4, "reps": 10, "weight": 100.0},
        {"id": 3, "name": "Pull-ups", "sets": 3, "reps": 10, "weight": None},
    ]


class TestRefreshConfig:
    """Tests for RefreshConfig."""

    def test_default_config(self):
        """Test default configuration values."""
        config = RefreshConfig()

        assert config.api_url == "http://localhost:8000"
        assert config.max_concurrency == 3
        assert config.max_retries == 3

    def test_custom_config(self, config):
        """Test custom configuration."""
        assert config.max_concurrency == 2
        assert config.retry_base_delay == 0.01


class TestRefreshResult:
    """Tests for RefreshResult."""

    def test_success_result(self):
        """Test creating a success result."""
        result = RefreshResult(
            exercise_id=1,
            success=True,
            message="OK",
            duration_ms=50.0
        )

        assert result.success is True
        assert result.retries == 0

    def test_failure_result(self):
        """Test creating a failure result."""
        result = RefreshResult(
            exercise_id=1,
            success=False,
            message="Connection error",
            duration_ms=100.0,
            retries=3
        )

        assert result.success is False
        assert result.retries == 3


class TestIdempotencyStore:
    """Tests for IdempotencyStore (in-memory fallback)."""

    @pytest.mark.anyio
    async def test_check_and_set_new_operation(self):
        """Test that new operations are allowed."""
        store = IdempotencyStore(redis_client=None, ttl=60)

        result = await store.check_and_set("refresh", 1)

        assert result is True

    @pytest.mark.anyio
    async def test_check_and_set_duplicate_operation(self):
        """Test that duplicate operations are blocked."""
        store = IdempotencyStore(redis_client=None, ttl=60)

        # First call should succeed
        result1 = await store.check_and_set("refresh", 1)
        assert result1 is True

        # Second call should be blocked
        result2 = await store.check_and_set("refresh", 1)
        assert result2 is False

    @pytest.mark.anyio
    async def test_different_operations_allowed(self):
        """Test that different operations are independent."""
        store = IdempotencyStore(redis_client=None, ttl=60)

        result1 = await store.check_and_set("refresh", 1)
        result2 = await store.check_and_set("refresh", 2)

        assert result1 is True
        assert result2 is True

    @pytest.mark.anyio
    async def test_mark_failed_allows_retry(self):
        """Test that marking as failed allows retry."""
        store = IdempotencyStore(redis_client=None, ttl=60)

        # First call
        await store.check_and_set("refresh", 1)

        # Mark as failed
        await store.mark_failed("refresh", 1)

        # Should be able to retry
        result = await store.check_and_set("refresh", 1)
        assert result is True

    @pytest.mark.anyio
    async def test_get_stats(self):
        """Test getting statistics."""
        store = IdempotencyStore(redis_client=None, ttl=60)

        await store.check_and_set("refresh", 1)
        await store.check_and_set("refresh", 2)

        stats = await store.get_stats()

        assert stats["store_type"] == "memory"
        assert stats["processed_count"] == 2


class TestExerciseRefresher:
    """Tests for ExerciseRefresher with mocked HTTP client."""

    @pytest.mark.anyio
    async def test_bounded_concurrency(self, config):
        """Test that concurrency is bounded by semaphore."""
        concurrent_count = 0
        max_concurrent = 0

        async def mock_request(*args, **kwargs):
            nonlocal concurrent_count, max_concurrent
            concurrent_count += 1
            max_concurrent = max(max_concurrent, concurrent_count)
            await asyncio.sleep(0.01)  # Simulate work
            concurrent_count -= 1

            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"id": 1, "name": "Test"}
            mock_response.raise_for_status = MagicMock()
            return mock_response

        refresher = ExerciseRefresher(config)
        refresher.http_client = MagicMock()
        refresher.http_client.get = mock_request
        refresher.idempotency = IdempotencyStore(None, ttl=60)

        exercises = [{"id": i, "name": f"Exercise {i}"} for i in range(10)]

        tasks = [refresher.refresh_exercise(ex) for ex in exercises]
        await asyncio.gather(*tasks)

        # Max concurrent should not exceed config
        assert max_concurrent <= config.max_concurrency

    @pytest.mark.anyio
    async def test_retry_on_failure(self, config):
        """Test retry logic on failures."""
        call_count = 0

        async def mock_request_failing(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise Exception("Simulated failure")

            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"id": 1, "name": "Test"}
            mock_response.raise_for_status = MagicMock()
            return mock_response

        refresher = ExerciseRefresher(config)
        refresher.http_client = MagicMock()
        refresher.http_client.get = mock_request_failing
        refresher.idempotency = IdempotencyStore(None, ttl=60)
        refresher.semaphore = asyncio.Semaphore(config.max_concurrency)

        result = await refresher.refresh_exercise({"id": 1, "name": "Test"})

        assert result.success is True
        assert result.retries == 1  # One retry was needed

    @pytest.mark.anyio
    async def test_idempotency_skip(self, config):
        """Test that already processed items are skipped."""
        refresher = ExerciseRefresher(config)
        refresher.http_client = MagicMock()
        refresher.idempotency = IdempotencyStore(None, ttl=60)
        refresher.semaphore = asyncio.Semaphore(config.max_concurrency)

        # Mark as already processed
        await refresher.idempotency.check_and_set("refresh", 1)

        result = await refresher.refresh_exercise({"id": 1, "name": "Test"})

        assert result.success is True
        assert "Skipped" in result.message
        assert refresher.skipped == 1

    @pytest.mark.anyio
    async def test_summary_stats(self, config):
        """Test summary statistics calculation."""
        refresher = ExerciseRefresher(config)
        refresher.processed = 8
        refresher.skipped = 2
        refresher.failed = 0
        refresher.total_duration_ms = 800.0

        summary = refresher.get_summary()

        assert summary["total"] == 10
        assert summary["success_rate"] == 100.0
        assert summary["avg_duration_ms"] == 100.0


class TestIntegration:
    """Integration-style tests (still mocked but testing flow)."""

    @pytest.mark.anyio
    async def test_full_refresh_flow(self, config, sample_exercises):
        """Test complete refresh flow with mocked client."""
        async def mock_get(path):
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.raise_for_status = MagicMock()

            if path == "/exercises":
                mock_response.json.return_value = sample_exercises
            else:
                # Individual exercise fetch
                exercise_id = int(path.split("/")[-1])
                mock_response.json.return_value = next(
                    (ex for ex in sample_exercises if ex["id"] == exercise_id),
                    None
                )
            return mock_response

        refresher = ExerciseRefresher(config)
        refresher.http_client = MagicMock()
        refresher.http_client.get = mock_get
        refresher.idempotency = IdempotencyStore(None, ttl=60)
        refresher.semaphore = asyncio.Semaphore(config.max_concurrency)

        results = await refresher.refresh_all()

        assert len(results) == 3
        assert all(r.success for r in results)
        assert refresher.processed == 3

