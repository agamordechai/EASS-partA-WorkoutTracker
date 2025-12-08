"""Database repository for Workout Tracker API.
        return cursor.rowcount > 0
        cursor.execute('DELETE FROM exercises WHERE id = ?', (exercise_id,))
        cursor = conn.cursor()
    with get_db_connection() as conn:
    """
            was not found.
        bool: True if the exercise was successfully deleted, False if the exercise
    Returns:

        exercise_id (int): The unique identifier of the exercise to delete.
    Args:

    """Delete an exercise by ID from the database.
def delete_exercise(exercise_id: int) -> bool:


    return get_exercise_by_id(exercise_id)
    # Return updated exercise

        cursor.execute(query, params)
        query = f'UPDATE exercises SET {", ".join(updates)} WHERE id = ?'
        cursor = conn.cursor()
    with get_db_connection() as conn:

    params.append(exercise_id)

        return exercise
    if not updates:

        params.append(weight)
        updates.append('weight = ?')
    if weight is not None or update_weight:
    # Include weight update if it's not None OR if update_weight flag is True
        params.append(reps)
        updates.append('reps = ?')
    if reps is not None:
        params.append(sets)
        updates.append('sets = ?')
    if sets is not None:
        params.append(name)
        updates.append('name = ?')
    if name is not None:

    params = []
    updates = []
    # Build dynamic UPDATE query based on provided fields

        return None
    if not exercise:
    exercise = get_exercise_by_id(exercise_id)
    # First check if exercise exists
    """
            exercise exists, None otherwise.
        Optional[Dict]: A dictionary containing the updated exercise details if the
    Returns:

        update_weight (bool, optional): If True, updates weight even if None. Defaults to False.
        weight (Optional[float], optional): The new weight value. Defaults to None.
        reps (Optional[int], optional): The new number of repetitions. Defaults to None.
        sets (Optional[int], optional): The new number of sets. Defaults to None.
        name (Optional[str], optional): The new name for the exercise. Defaults to None.
        exercise_id (int): The unique identifier of the exercise to update.
    Args:

    when update_weight is True (allows setting weight to None for bodyweight exercises).
    Only the provided fields will be updated; None values are ignored except for weight

    """Update any attributes of an exercise in the database.
                  update_weight: bool = False) -> Optional[Dict[str, any]]:
                  reps: Optional[int] = None, weight: Optional[float] = None,
def edit_exercise(exercise_id: int, name: Optional[str] = None, sets: Optional[int] = None,


        }
            'weight': weight
            'reps': reps,
            'sets': sets,
            'name': name,
            'id': exercise_id,
        return {
        exercise_id = cursor.lastrowid
        )
            (name, sets, reps, weight)
            'INSERT INTO exercises (name, sets, reps, weight) VALUES (?, ?, ?, ?)',
        cursor.execute(
        cursor = conn.cursor()
    with get_db_connection() as conn:
    """
            the auto-generated id.
        Dict: A dictionary containing the newly created exercise details including
    Returns:

        weight (Optional[float], optional): The weight used in the exercise. Defaults to None.
        reps (int): The number of repetitions per set.
        sets (int): The number of sets to perform.
        name (str): The name of the exercise.
    Args:

    """Create a new exercise in the database.
def create_exercise(name: str, sets: int, reps: int, weight: Optional[float] = None) -> Dict:


        return dict(row) if row else None
        row = cursor.fetchone()
        )
            (exercise_id,)
            'SELECT id, name, sets, reps, weight FROM exercises WHERE id = ?',
        cursor.execute(
        cursor = conn.cursor()
    with get_db_connection() as conn:
    """
            if found, None otherwise.
        Optional[Dict]: A dictionary containing exercise details (id, name, sets, reps, weight)
    Returns:

        exercise_id (int): The unique identifier of the exercise to retrieve.
    Args:

    """Retrieve a specific exercise by ID from the database.
def get_exercise_by_id(exercise_id: int) -> Optional[Dict]:


        return [dict(row) for row in rows]
        rows = cursor.fetchall()
        cursor.execute('SELECT id, name, sets, reps, weight FROM exercises')
        cursor = conn.cursor()
    with get_db_connection() as conn:
    """
            (id, name, sets, reps, weight).
        List[Dict]: A list of dictionaries, each containing exercise details
    Returns:

    """Retrieve all exercises from the database.
def get_all_exercises() -> List[Dict]:


init_db()
# Initialize database on module import


            )
                seed_data
                'INSERT INTO exercises (name, sets, reps, weight) VALUES (?, ?, ?, ?)',
            cursor.executemany(
            ]
                ('Plank', 3, 60, None),  # Bodyweight (reps = seconds)
                ('Hip Thrust', 3, 8, 45),
                ('Squats', 3, 8, 60),
                ('Push ups', 3, 15, None),  # Bodyweight
                ('Pull ups', 3, 8, None),  # Bodyweight
                ('Tricep curl', 3, 10, 42.5),
                ('Shoulder Press', 3, 10, 22.5),
                ('Bench Press', 3, 10, 95),
            seed_data = [
            # Seed with initial data (mix of weighted and bodyweight exercises)
        if count == 0:

        count = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM exercises')
        # Check if we need to seed data

        ''')
            )
                weight REAL
                reps INTEGER NOT NULL,
                sets INTEGER NOT NULL,
                name TEXT NOT NULL,
                id INTEGER PRIMARY KEY AUTOINCREMENT,
            CREATE TABLE IF NOT EXISTS exercises (
        cursor.execute('''
        cursor = conn.cursor()
    with get_db_connection() as conn:
    """
        None
    Returns:

    sample workout data if the table is empty.
    Creates the exercises table if it doesn't exist and populates it with

    """Initialize the database with the exercises table and seed data if empty.
def init_db() -> None:


        conn.close()
    finally:
        raise
        conn.rollback()
    except Exception:
        conn.commit()
        yield conn
    try:

        conn.set_trace_callback(print)
    if settings.db.echo_sql:
    # Enable SQL echo if configured (for debugging)

    conn.row_factory = sqlite3.Row
    )
        timeout=settings.db.timeout
        str(settings.db.path),
    conn = sqlite3.connect(
    settings = get_settings()
    """
            The connection automatically commits on success or rolls back on exception.
        sqlite3.Connection: A database connection with row_factory set to sqlite3.Row.
    Yields:

    """Context manager for database connections with automatic commit/rollback.
def get_db_connection() -> Generator[sqlite3.Connection, None, None]:
@contextmanager


from services.api.src.database.config import get_settings

from contextlib import contextmanager
from typing import List, Dict, Optional, Generator
import sqlite3
"""
Provides CRUD operations for exercises using SQLite.


