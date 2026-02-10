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


def seed_exercises(count: int = 27) -> None:
    """Seed the database with sample exercises.

    Args:
        count: Number of exercises to create (max 27)
    """
    sample_exercises = [
        {"name": "Bench Press", "sets": 3, "reps": 10, "weight": 100.0, "workout_day": "A"},
        {"name": "Shoulder Press", "sets": 3, "reps": 10, "weight": 22.5, "workout_day": "A"},
        {"name": "Tricep curl", "sets": 3, "reps": 10, "weight": 42.5, "workout_day": "A"},
        {"name": "Pull ups", "sets": 5, "reps": 8, "weight": None, "workout_day": "B"},
        {"name": "Squats", "sets": 3, "reps": 8, "weight": 95.0, "workout_day": "C"},
        {"name": "Hip Thrust", "sets": 3, "reps": 10, "weight": 100.0, "workout_day": "C"},
        {"name": "Bulgarian Split Squat", "sets": 3, "reps": 8, "weight": 27.5, "workout_day": "C"},
        {"name": "Hip Adduction", "sets": 3, "reps": 16, "weight": 90.0, "workout_day": "C"},
        {"name": "Hip Abduction", "sets": 3, "reps": 16, "weight": 90.0, "workout_day": "C"},
        {"name": "Incline Bench Press", "sets": 3, "reps": 10, "weight": 37.5, "workout_day": "A"},
        {"name": "Chest Fly", "sets": 3, "reps": 10, "weight": 20.0, "workout_day": "A"},
        {"name": "Upper Chest Fly", "sets": 3, "reps": 10, "weight": 20.0, "workout_day": "A"},
        {"name": "Shoulder Extention", "sets": 5, "reps": 8, "weight": 12.5, "workout_day": "A"},
        {"name": "Overhead Tricep curl", "sets": 3, "reps": 8, "weight": 17.5, "workout_day": "A"},
        {"name": "Cable Row", "sets": 3, "reps": 12, "weight": 80.0, "workout_day": "B"},
        {"name": "Pull Over", "sets": 3, "reps": 10, "weight": 45.0, "workout_day": "B"},
        {"name": "Dumble Shrugs", "sets": 3, "reps": 12, "weight": 35.0, "workout_day": "B"},
        {"name": "Rear Delt", "sets": 3, "reps": 10, "weight": 10.0, "workout_day": "B"},
        {"name": "Bicep Curl", "sets": 3, "reps": 10, "weight": 35.0, "workout_day": "B"},
        {"name": "Bicep Hammer Curls", "sets": 3, "reps": 8, "weight": 25.0, "workout_day": "B"},
        {"name": "Knee Extention", "sets": 3, "reps": 10, "weight": 164.0, "workout_day": "C"},
        {"name": "Knee Flexion", "sets": 3, "reps": 10, "weight": 90.0, "workout_day": "C"},
        {"name": "Crunches", "sets": 1, "reps": 30, "weight": None, "workout_day": "None"},
        {"name": "Penguins", "sets": 1, "reps": 25, "weight": None, "workout_day": "None"},
        {"name": "Leg drops", "sets": 1, "reps": 25, "weight": None, "workout_day": "None"},
        {"name": "Plank", "sets": 1, "reps": 90, "weight": None, "workout_day": "None"},
        {"name": "Running", "sets": 1, "reps": 30, "weight": None, "workout_day": "None"},
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
        default=27,
        help="Number of exercises to create (default: 27, max: 27)"
    )

    args = parser.parse_args()
    seed_exercises(args.count)

