"""FastAPI dependencies for database access.

Provides dependency injection for database sessions and repositories.
"""
from typing import Annotated
from fastapi import Depends
from sqlmodel import Session

from services.api.src.database.database import get_session
from services.api.src.database.sqlmodel_repository import ExerciseRepository


def get_exercise_repository(
    session: Annotated[Session, Depends(get_session)]
) -> ExerciseRepository:
    """Provide an ExerciseRepository instance.

    This is a FastAPI dependency that creates a repository
    with the current database session.

    Args:
        session: SQLModel session from dependency injection

    Returns:
        ExerciseRepository: Repository instance for exercise operations
    """
    return ExerciseRepository(session)


# Type alias for dependency injection
SessionDep = Annotated[Session, Depends(get_session)]
RepositoryDep = Annotated[ExerciseRepository, Depends(get_exercise_repository)]