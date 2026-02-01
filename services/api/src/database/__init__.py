"""Database module for Workout Tracker API - SQLModel version."""
from services.api.src.database.database import init_db, get_session, engine
from services.api.src.database.db_models import ExerciseTable
from services.api.src.database.sqlmodel_repository import ExerciseRepository
from services.api.src.database.dependencies import RepositoryDep, SessionDep
from services.api.src.database.models import Exercise, ExerciseResponse, ExerciseEditRequest

__all__ = [
    # SQLModel components
    "init_db",
    "get_session",
    "engine",
    "ExerciseTable",
    "ExerciseRepository",
    "RepositoryDep",
    "SessionDep",
    # Pydantic models
    "Exercise",
    "ExerciseResponse",
    "ExerciseEditRequest",
]

