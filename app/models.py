from pydantic import BaseModel
from typing import Optional

class Exercise(BaseModel):
    """Exercise model for creating new exercises.

    Attributes:
        name (str): The name of the exercise.
        sets (int): The number of sets to perform.
        reps (int): The number of repetitions per set.
        weight (Optional[float]): The weight used in the exercise (optional).
    """
    name: str
    sets: int
    reps: int
    weight: Optional[float] = None

class ExerciseResponse(BaseModel):
    """Exercise response model for returning exercise data.

    Attributes:
        id (int): The unique identifier of the exercise.
        name (str): The name of the exercise.
        sets (int): The number of sets to perform.
        reps (int): The number of repetitions per set.
        weight (Optional[float]): The weight used in the exercise (optional).
    """
    id: int
    name: str
    sets: int
    reps: int
    weight: Optional[float] = None

class ExerciseEditRequest(BaseModel):
    """Exercise edit request model for updating exercises.

    All attributes are optional to allow partial updates of exercise data.

    Attributes:
        name (Optional[str]): The new name for the exercise (optional).
        sets (Optional[int]): The new number of sets (optional).
        reps (Optional[int]): The new number of repetitions (optional).
        weight (Optional[float]): The new weight value (optional).
    """
    name: Optional[str] = None
    sets: Optional[int] = None
    reps: Optional[int] = None
    weight: Optional[float] = None
