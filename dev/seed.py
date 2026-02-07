#!/usr/bin/env python
"""Seed script for populating the database with sample exercises.

This script provides a simple way to populate the database with sample
workout exercises for testing and development using SQLModel.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from services.api.src.database.database import init_db, get_session
from services.api.src.database.sqlmodel_repository import ExerciseRepository


def seed_exercises(count: int = 10) -> None:
    """Seed the database with sample exercises.

    Args:
        count: Number of exercises to create (max 10)
    """
    sample_exercises = [
        {"name": "Bench Press", "sets": 4, "reps": 8, "weight": 80.0, "workout_day": "A"},
        {"name": "Squat", "sets": 4, "reps": 10, "weight": 100.0, "workout_day": "B"},
        {"name": "Deadlift", "sets": 3, "reps": 5, "weight": 120.0, "workout_day": "B"},
        {"name": "Pull-ups", "sets": 3, "reps": 12, "weight": None, "workout_day": "C"},
        {"name": "Overhead Press", "sets": 3, "reps": 10, "weight": 50.0, "workout_day": "A"},
        {"name": "Barbell Row", "sets": 4, "reps": 10, "weight": 70.0, "workout_day": "C"},
        {"name": "Dips", "sets": 3, "reps": 15, "weight": None, "workout_day": "A"},
        {"name": "Lunges", "sets": 3, "reps": 12, "weight": 30.0, "workout_day": "B"},
        {"name": "Push-ups", "sets": 3, "reps": 20, "weight": None, "workout_day": "A"},
        {"name": "Bicep Curls", "sets": 3, "reps": 12, "weight": 15.0, "workout_day": "C"},
    ]

    # Initialize database tables if needed
    init_db()
    print("Database initialized")

    exercises_to_create = min(count, len(sample_exercises))
    print(f"Creating {exercises_to_create} sample exercises...")

    with next(get_session()) as session:
        repo = ExerciseRepository(session)

        for i in range(exercises_to_create):
            exercise_data = sample_exercises[i]
            exercise = repo.create(**exercise_data)
            weight_str = f"{exercise.weight} kg" if exercise.weight else "Bodyweight"
            print(f"  ✓ Created: {exercise.name} ({exercise.sets}x{exercise.reps}, {weight_str}) - Day {exercise.workout_day}")

        # Count all exercises
        all_exercises = repo.get_all()
        print(f"\nDone! Total exercises in database: {len(all_exercises)}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Seed the database with sample exercises (SQLModel)")
    parser.add_argument(
        "--count", "-c",
        type=int,
        default=10,
        help="Number of exercises to create (default: 10, max: 10)"
    )

    args = parser.parse_args()
    seed_exercises(args.count)

