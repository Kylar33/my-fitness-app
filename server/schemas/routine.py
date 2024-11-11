from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ExerciseBase(BaseModel):
    name: str
    description: Optional[str] = None
    sets: int
    reps: int
    rest_time: int

class ExerciseCreate(ExerciseBase):
    pass

class Exercise(ExerciseBase):
    id: int
    routine_id: int
    created_at: datetime

    class Config:
        orm_mode = True

class RoutineBase(BaseModel):
    name: str
    description: Optional[str] = None

class RoutineCreate(RoutineBase):
    exercises: List[ExerciseCreate]

class Routine(RoutineBase):
    id: int
    trainer_id: int
    created_at: datetime
    exercises: List[Exercise]

    class Config:
        orm_mode = True