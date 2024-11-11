from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class MealBase(BaseModel):
    name: str
    description: Optional[str] = None
    calories: float
    protein: float
    carbs: float
    fats: float
    time_of_day: str

class MealCreate(MealBase):
    pass

class Meal(MealBase):
    id: int
    nutrition_plan_id: int
    created_at: datetime

    class Config:
        orm_mode = True

class NutritionPlanBase(BaseModel):
    name: str
    description: Optional[str] = None

class NutritionPlanCreate(NutritionPlanBase):
    meals: List[MealCreate]

class NutritionPlan(NutritionPlanBase):
    id: int
    trainer_id: int
    created_at: datetime
    meals: List[Meal]

    class Config:
        orm_mode = True