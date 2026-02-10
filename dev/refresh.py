#!/usr/bin/env python3
"""Async refresh script for Session 09.

This script demonstrates:
- Bounded concurrency using asyncio.Semaphore
- Retry logic with exponential backoff
- Redis-backed idempotency to prevent duplicate processing
- Async HTTP requests with httpx

Usage:
    uv run python scripts/refresh.py
    uv run python scripts/refresh.py --concurrency 5 --api-url http://localhost:8000
"""
from __future__ import annotations

import asyncio
import argparse
import logging
import sys
from dataclasses import dataclass
from datetime import datetime, timezone

import httpx

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class RefreshConfig:
    """Configuration for the refresh process."""
    api_url: str = "http://localhost:8000"
    redis_url: str = "redis://localhost:6379/0"
    max_concurrency: int = 3
    max_retries: int = 3
    retry_base_delay: float = 1.0
    idempotency_ttl: int = 3600  # 1 hour
    timeout: float = 10.0


@dataclass
class RefreshResult:
    """Result of a refresh operation."""
    exercise_id: int
    success: bool
    message: str
    duration_ms: float
    retries: int = 0


class IdempotencyStore:
    """Redis-backed idempotency store to prevent duplicate processing."""

    def __init__(self, redis_client: redis.Redis | None, ttl: int = 3600):
        """Initialize the idempotency store.

        Args:
            redis_client: Redis client instance (can be None for in-memory fallback)
            ttl: Time-to-live for idempotency keys in seconds
        """
        self.redis = redis_client
        self.ttl = ttl
        self._memory_store: dict[str, str] = {}  # Fallback if Redis unavailable

    def _make_key(self, operation: str, resource_id: int) -> str:
        """Create an idempotency key.

        Args:
            operation: Operation name (e.g., 'refresh')
            resource_id: Resource ID being processed

        Returns:
            Idempotency key string
        """
        # Include date to allow daily re-processing
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        return f"idempotency:{operation}:{resource_id}:{date_str}"

    async def check_and_set(self, operation: str, resource_id: int) -> bool:
        """Check if operation was already processed, and mark as processed if not.

        Args:
            operation: Operation name
            resource_id: Resource ID

        Returns:
            True if operation should proceed (not previously processed)
            False if operation was already processed (skip)
        """
        key = self._make_key(operation, resource_id)

        if self.redis:
            try:
                # SETNX returns True if key was set, False if it already existed
                result = await self.redis.set(key, "processed", nx=True, ex=self.ttl)
                return result is not None
            except Exception as e:
                logger.warning(f"Redis error, falling back to memory: {e}")

        # Fallback to in-memory store
        if key in self._memory_store:
            return False
        self._memory_store[key] = "processed"
        return True

    async def mark_failed(self, operation: str, resource_id: int) -> None:
        """Remove idempotency key to allow retry on failure.

        Args:
            operation: Operation name
            resource_id: Resource ID
        """
        key = self._make_key(operation, resource_id)

        if self.redis:
            try:
                await self.redis.delete(key)
            except Exception as e:
                logger.warning(f"Redis error removing key: {e}")
        else:
            self._memory_store.pop(key, None)

    async def get_stats(self) -> dict:
        """Get statistics about processed operations.

        Returns:
            Dictionary with stats
        """
        if self.redis:
            try:
                keys = await self.redis.keys("idempotency:*")
                return {
                    "store_type": "redis",
                    "processed_count": len(keys),
                    "ttl_seconds": self.ttl
                }
            except Exception:
                pass

        return {
            "store_type": "memory",
            "processed_count": len(self._memory_store),
            "ttl_seconds": self.ttl
        }


class ExerciseRefresher:
    """Async exercise refresher with bounded concurrency and retries."""

    def __init__(self, config: RefreshConfig):
        """Initialize the refresher.

        Args:
            config: Refresh configuration
        """
        self.config = config
        self.semaphore = asyncio.Semaphore(config.max_concurrency)
        self.http_client: httpx.AsyncClient | None = None
        self.redis_client: redis.Redis | None = None
        self.idempotency: IdempotencyStore | None = None

        # Stats
        self.processed = 0
        self.skipped = 0
        self.failed = 0
        self.total_duration_ms = 0.0

    async def __aenter__(self):
        """Async context manager entry."""
        self.http_client = httpx.AsyncClient(
            base_url=self.config.api_url,
            timeout=self.config.timeout
        )

        # Try to connect to Redis
        if REDIS_AVAILABLE:
            try:
                self.redis_client = redis.from_url(
                    self.config.redis_url,
                    decode_responses=True
                )
                await self.redis_client.ping()
                logger.info(f"Connected to Redis at {self.config.redis_url}")
            except Exception as e:
                logger.warning(f"Redis connection failed: {e}. Using in-memory idempotency.")
                self.redis_client = None
        else:
            logger.warning("Redis package not installed. Using in-memory idempotency.")

        self.idempotency = IdempotencyStore(
            self.redis_client,
            ttl=self.config.idempotency_ttl
        )

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.http_client:
            await self.http_client.aclose()
        if self.redis_client:
            await self.redis_client.aclose()

    async def fetch_exercises(self) -> list[dict]:
        """Fetch all exercises from the API.

        Returns:
            List of exercise dictionaries
        """
        try:
            response = await self.http_client.get("/exercises")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to fetch exercises: {e}")
            return []

    async def refresh_exercise(self, exercise: dict) -> RefreshResult:
        """Refresh a single exercise with retry logic.

        Args:
            exercise: Exercise data dictionary

        Returns:
            RefreshResult with operation outcome
        """
        exercise_id = exercise["id"]
        start_time = asyncio.get_event_loop().time()
        retries = 0

        async with self.semaphore:  # Bounded concurrency
            # Check idempotency
            should_process = await self.idempotency.check_and_set("refresh", exercise_id)
            if not should_process:
                duration_ms = (asyncio.get_event_loop().time() - start_time) * 1000
                self.skipped += 1
                return RefreshResult(
                    exercise_id=exercise_id,
                    success=True,
                    message="Skipped (already processed today)",
                    duration_ms=duration_ms
                )

            # Process with retries
            last_error = None
            for attempt in range(self.config.max_retries):
                try:
                    retries = attempt

                    # Simulate refresh operation - in real scenario this might:
                    # - Recalculate volume
                    # - Update recommendations
                    # - Sync with external services
                    # For demo, we just verify the exercise exists
                    response = await self.http_client.get(f"/exercises/{exercise_id}")
                    response.raise_for_status()

                    duration_ms = (asyncio.get_event_loop().time() - start_time) * 1000
                    self.processed += 1
                    self.total_duration_ms += duration_ms

                    logger.info(
                        f"[OK] Exercise {exercise_id} ({exercise['name']}) "
                        f"refreshed in {duration_ms:.2f}ms"
                    )

                    return RefreshResult(
                        exercise_id=exercise_id,
                        success=True,
                        message=f"Refreshed successfully",
                        duration_ms=duration_ms,
                        retries=retries
                    )

                except httpx.HTTPStatusError as e:
                    last_error = e
                    if e.response.status_code == 404:
                        # Don't retry 404s
                        break
                    logger.warning(
                        f"[RETRY {attempt + 1}/{self.config.max_retries}] "
                        f"Exercise {exercise_id}: HTTP {e.response.status_code}"
                    )
                except Exception as e:
                    last_error = e
                    logger.warning(
                        f"[RETRY {attempt + 1}/{self.config.max_retries}] "
                        f"Exercise {exercise_id}: {e}"
                    )

                # Exponential backoff
                if attempt < self.config.max_retries - 1:
                    delay = self.config.retry_base_delay * (2 ** attempt)
                    await asyncio.sleep(delay)

            # All retries failed - mark for re-processing
            await self.idempotency.mark_failed("refresh", exercise_id)

            duration_ms = (asyncio.get_event_loop().time() - start_time) * 1000
            self.failed += 1

            return RefreshResult(
                exercise_id=exercise_id,
                success=False,
                message=f"Failed after {self.config.max_retries} attempts: {last_error}",
                duration_ms=duration_ms,
                retries=retries
            )

    async def refresh_all(self) -> list[RefreshResult]:
        """Refresh all exercises with bounded concurrency.

        Returns:
            List of refresh results
        """
        exercises = await self.fetch_exercises()

        if not exercises:
            logger.warning("No exercises to refresh")
            return []

        logger.info(
            f"Starting refresh of {len(exercises)} exercises "
            f"(max concurrency: {self.config.max_concurrency})"
        )

        # Create tasks for all exercises
        tasks = [
            self.refresh_exercise(exercise)
            for exercise in exercises
        ]

        # Execute with bounded concurrency (semaphore handles this)
        results = await asyncio.gather(*tasks)

        return list(results)

    def get_summary(self) -> dict:
        """Get summary statistics.

        Returns:
            Dictionary with summary stats
        """
        return {
            "processed": self.processed,
            "skipped": self.skipped,
            "failed": self.failed,
            "total": self.processed + self.skipped + self.failed,
            "avg_duration_ms": (
                self.total_duration_ms / self.processed
                if self.processed > 0 else 0
            ),
            "success_rate": (
                (self.processed + self.skipped) / (self.processed + self.skipped + self.failed) * 100
                if (self.processed + self.skipped + self.failed) > 0 else 0
            )
        }


async def main(config: RefreshConfig) -> int:
    """Main entry point for the refresh script.

    Args:
        config: Refresh configuration

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    logger.info("=" * 60)
    logger.info("Exercise Refresh Script - Session 09")
    logger.info("=" * 60)
    logger.info(f"API URL: {config.api_url}")
    logger.info(f"Redis URL: {config.redis_url}")
    logger.info(f"Max Concurrency: {config.max_concurrency}")
    logger.info(f"Max Retries: {config.max_retries}")
    logger.info("=" * 60)

    start_time = datetime.now(timezone.utc)

    async with ExerciseRefresher(config) as refresher:
        # Get idempotency stats
        idempotency_stats = await refresher.idempotency.get_stats()
        logger.info(f"Idempotency store: {idempotency_stats['store_type']}")

        # Run refresh
        results = await refresher.refresh_all()

        # Print summary
        summary = refresher.get_summary()

        logger.info("=" * 60)
        logger.info("REFRESH COMPLETE")
        logger.info("=" * 60)
        logger.info(f"Processed: {summary['processed']}")
        logger.info(f"Skipped (idempotent): {summary['skipped']}")
        logger.info(f"Failed: {summary['failed']}")
        logger.info(f"Total: {summary['total']}")
        logger.info(f"Success Rate: {summary['success_rate']:.1f}%")
        logger.info(f"Avg Duration: {summary['avg_duration_ms']:.2f}ms")
        logger.info(f"Total Time: {(datetime.now(timezone.utc) - start_time).total_seconds():.2f}s")
        logger.info("=" * 60)

        # Return success if no failures
        return 0 if summary['failed'] == 0 else 1


def parse_args() -> RefreshConfig:
    """Parse command line arguments.

    Returns:
        RefreshConfig with parsed values
    """
    parser = argparse.ArgumentParser(
        description="Async exercise refresh with bounded concurrency"
    )
    parser.add_argument(
        "--api-url",
        default="http://localhost:8000",
        help="Workout API URL (default: http://localhost:8000)"
    )
    parser.add_argument(
        "--redis-url",
        default="redis://localhost:6379/0",
        help="Redis URL for idempotency (default: redis://localhost:6379/0)"
    )
    parser.add_argument(
        "--concurrency", "-c",
        type=int,
        default=3,
        help="Max concurrent requests (default: 3)"
    )
    parser.add_argument(
        "--retries", "-r",
        type=int,
        default=3,
        help="Max retries per request (default: 3)"
    )
    parser.add_argument(
        "--timeout", "-t",
        type=float,
        default=10.0,
        help="Request timeout in seconds (default: 10.0)"
    )

    args = parser.parse_args()

    return RefreshConfig(
        api_url=args.api_url,
        redis_url=args.redis_url,
        max_concurrency=args.concurrency,
        max_retries=args.retries,
        timeout=args.timeout
    )


if __name__ == "__main__":
    config = parse_args()
    exit_code = asyncio.run(main(config))
    sys.exit(exit_code)

