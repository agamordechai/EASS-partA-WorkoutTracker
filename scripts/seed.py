#!/usr/bin/env python
"""Seed script for populating the database with sample exercises.

This script provides a simple way to populate the database with sample
workout exercises for testing and development.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from services.api.src.database.repository import create_exercise, get_all_exercises


def seed_exercises(count: int = 10) -> None:
    """Seed the database with sample exercises.

    Args:
        count: Number of exercises to create (max 10)
    """
    sample_exercises = [
        {"name": "Bench Press", "sets": 4, "reps": 8, "weight": 80.0},
        {"name": "Squat", "sets": 4, "reps": 10, "weight": 100.0},
        {"name": "Deadlift", "sets": 3, "reps": 5, "weight": 120.0},
        {"name": "Pull-ups", "sets": 3, "reps": 12, "weight": None},
        {"name": "Overhead Press", "sets": 3, "reps": 10, "weight": 50.0},
        {"name": "Barbell Row", "sets": 4, "reps": 10, "weight": 70.0},
        {"name": "Dips", "sets": 3, "reps": 15, "weight": None},
        {"name": "Lunges", "sets": 3, "reps": 12, "weight": 30.0},
        {"name": "Push-ups", "sets": 3, "reps": 20, "weight": None},
        {"name": "Bicep Curls", "sets": 3, "reps": 12, "weight": 15.0},
    ]

    exercises_to_create = min(count, len(sample_exercises))

    print(f"Creating {exercises_to_create} sample exercises...")

    for i in range(exercises_to_create):
        exercise_data = sample_exercises[i]
        exercise = create_exercise(**exercise_data)
        weight_str = f"{exercise['weight']} kg" if exercise.get('weight') else "Bodyweight"
        print(f"  ✓ Created: {exercise['name']} ({exercise['sets']}x{exercise['reps']}, {weight_str})")

    print(f"\nDone! Total exercises in database: {len(get_all_exercises())}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Seed the database with sample exercises")
    parser.add_argument(
        "--count", "-c",
        type=int,
        default=10,
        help="Number of exercises to create (default: 10, max: 10)"
    )

    args = parser.parse_args()
    seed_exercises(args.count)

