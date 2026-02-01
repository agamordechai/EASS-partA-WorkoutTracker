"""SQLModel database table definitions for Workout Tracker.

This module defines the database tables using SQLModel ORM.
Separate from Pydantic models to maintain clear separation between
database layer and API layer.
"""
from typing import Optional
from sqlmodel import Field, SQLModel


class ExerciseTable(SQLModel, table=True):
    """Exercise database table model.

    This SQLModel class represents the 'exercises' table in the database.
    It uses SQLModel which combines SQLAlchemy ORM with Pydantic validation.

    Attributes:
        id: Auto-incrementing primary key
        name: Exercise name (required, max 100 chars)
        sets: Number of sets (required, 1-100)
        reps: Number of repetitions (required, 1-1000)
        weight: Weight in kg (optional for bodyweight exercises)
        workout_day: Workout day identifier (A-G or 'None')
    """

    __tablename__ = "exercises"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100, index=True)
    sets: int = Field(ge=1, le=100)
    reps: int = Field(ge=1, le=1000)
    weight: Optional[float] = Field(default=None, ge=0)
    workout_day: str = Field(default='A', max_length=10)