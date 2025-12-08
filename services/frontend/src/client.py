"""Typed HTTP client for the Workout Tracker API.

This module provides a clean interface for consuming the FastAPI backend
from UI components (Streamlit, Typer CLI, etc.).
"""

from __future__ import annotations

from functools import lru_cache
from typing import Any

import httpx
from pydantic_settings import BaseSettings, SettingsConfigDict


class UISettings(BaseSettings):
    """Configuration settings for the UI layer.

    Attributes:
        api_base_url (str): Base URL for the FastAPI backend. Defaults to http://localhost:8000
        trace_id (str): Identifier for tracing UI requests. Defaults to ui-streamlit
    """
    api_base_url: str = "http://localhost:8000"
    trace_id: str = "ui-streamlit"

    model_config = SettingsConfigDict(
        env_prefix="WORKOUT_",
        env_file=".env",
        extra="ignore"
    )


settings = UISettings()


@lru_cache(maxsize=1)
def _client() -> httpx.Client:
    """Get a cached HTTP client instance.

    Returns:
        httpx.Client: Configured HTTP client with base URL, trace headers, and timeout.
    """
    return httpx.Client(
        base_url=settings.api_base_url,
        headers={"X-Trace-Id": settings.trace_id},
        timeout=10.0,
    )


def list_exercises() -> list[dict[str, Any]]:
    """Fetch all exercises from the API.

    Returns:
        list[dict[str, Any]]: List of exercise dictionaries containing id, name, sets, reps, and weight.

    Raises:
        httpx.HTTPStatusError: If the API returns a non-2xx status code.
    """
    response = _client().get("/exercises")
    response.raise_for_status()
    return response.json()


def get_exercise(exercise_id: int) -> dict[str, Any]:
    """Fetch a specific exercise by ID.

    Args:
        exercise_id (int): The unique identifier of the exercise.

    Returns:
        dict[str, Any]: Exercise dictionary containing id, name, sets, reps, and weight.

    Raises:
        httpx.HTTPStatusError: If the API returns a non-2xx status code or exercise not found.
    """
    response = _client().get(f"/exercises/{exercise_id}")
    response.raise_for_status()
    return response.json()


def create_exercise(
    *,
    name: str,
    sets: int,
    reps: int,
    weight: float | None = None
) -> dict[str, Any]:
    """Create a new exercise in the tracker.

    Args:
        name (str): The name of the exercise (e.g., "Bench Press").
        sets (int): The number of sets to perform.
        reps (int): The number of repetitions per set.
        weight (float | None): The weight used in kg or lbs. Optional.

    Returns:
        dict[str, Any]: The newly created exercise with its assigned ID.

    Raises:
        httpx.HTTPStatusError: If the API returns a non-2xx status code.
    """
    payload = {
        "name": name,
        "sets": sets,
        "reps": reps,
    }
    if weight is not None:
        payload["weight"] = weight

    response = _client().post("/exercises", json=payload)
    response.raise_for_status()
    return response.json()


def update_exercise(
    exercise_id: int,
    *,
    name: str | None = None,
    sets: int | None = None,
    reps: int | None = None,
    weight: float | None = None
) -> dict[str, Any]:
    """Update an existing exercise (partial update).

    Args:
        exercise_id (int): The unique identifier of the exercise to update.
        name (str | None): New name for the exercise. Optional.
        sets (int | None): New number of sets. Optional.
        reps (int | None): New number of reps. Optional.
        weight (float | None): New weight value. Optional. Can be None to set as bodyweight.

    Returns:
        dict[str, Any]: The updated exercise data.

    Raises:
        httpx.HTTPStatusError: If the API returns a non-2xx status code or exercise not found.
    """
    payload = {}
    if name is not None:
        payload["name"] = name
    if sets is not None:
        payload["sets"] = sets
    if reps is not None:
        payload["reps"] = reps
    # Note: We don't check if weight is not None here because the dashboard
    # always calls this with all parameters when updating, and we want to support
    # setting weight to None (bodyweight). The API will detect if weight was provided.
    payload["weight"] = weight

    response = _client().patch(f"/exercises/{exercise_id}", json=payload)
    response.raise_for_status()
    return response.json()


def delete_exercise(exercise_id: int) -> None:
    """Delete an exercise from the tracker.

    Args:
        exercise_id (int): The unique identifier of the exercise to delete.

    Raises:
        httpx.HTTPStatusError: If the API returns a non-2xx status code or exercise not found.
    """
    response = _client().delete(f"/exercises/{exercise_id}")
    response.raise_for_status()

