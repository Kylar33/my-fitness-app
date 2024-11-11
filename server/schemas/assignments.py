from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

class AssignmentBase(BaseModel):
    start_date: date
    end_date: Optional[date] = None

class RoutineAssignment(AssignmentBase):
    user_id: int
    routine_id: int

class NutritionPlanAssignment(AssignmentBase):
    user_id: int
    nutrition_plan_id: int

class AssignmentResponse(AssignmentBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True