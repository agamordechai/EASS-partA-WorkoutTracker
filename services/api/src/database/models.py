"""Pydantic models (schemas) for the Workout Tracker API.

This module imports shared exercise models and defines API-specific models.
The shared models ensure consistency across all microservices.
"""
from pydantic import BaseModel, Field
from typing import Dict, Any

# Import shared exercise models (single source of truth)
from services.shared.models import (
    ExerciseBase as Exercise,
    ExerciseResponse,
    ExerciseEditRequest,
    PaginatedExerciseResponse,
)

# Re-export for backward compatibility
__all__ = [
    "Exercise",
    "ExerciseResponse",
    "ExerciseEditRequest",
    "PaginatedExerciseResponse",
    "HealthResponse",
]


class HealthResponse(BaseModel):
    """Health check response model.

    Attributes:
        status (str): Overall health status ('healthy' or 'unhealthy').
        version (str): API version string.
        timestamp (str): ISO 8601 timestamp of the health check.
        database (Dict[str, Any]): Database connectivity information.
    """
    status: str = Field(..., description="Health status: 'healthy' or 'unhealthy'")
    version: str = Field(..., description="API version")
    timestamp: str = Field(..., description="ISO 8601 timestamp")
    database: Dict[str, Any] = Field(..., description="Database status info")
