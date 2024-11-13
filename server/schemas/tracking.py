from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime

class ProgressTrackingBase(BaseModel):
    weight: float
    height: float
    body_fat: Optional[float] = None
    muscle_mass: Optional[float] = None
    notes: Optional[str] = None
    tracking_date: date

class ProgressTrackingCreate(ProgressTrackingBase):
    user_id: int

class ProgressTracking(ProgressTrackingBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

class WorkoutLogBase(BaseModel):
    routine_id: int
    exercise_id: int
    sets_completed: int
    reps_completed: int
    weight_used: float
    notes: Optional[str] = None
    workout_date: date

class WorkoutLogCreate(WorkoutLogBase):
    user_id: int

class WorkoutLog(WorkoutLogBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True