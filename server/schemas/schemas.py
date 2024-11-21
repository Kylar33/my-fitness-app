from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from datetime import date, datetime

# Base schemas para Exercise y Meal (necesarios para otras clases)
class ExerciseBase(BaseModel):
    name: str
    sets: int
    reps: int

class ExerciseCreate(ExerciseBase):
    pass

class Exercise(ExerciseBase):
    id: int
    workout_plan_id: Optional[int] = None
    routine_id: Optional[int] = None

    class Config:
        from_attributes = True

class MealBase(BaseModel):
    name: str
    description: Optional[str] = None
    calories: int

class MealCreate(MealBase):
    pass

class Meal(MealBase):
    id: int
    nutrition_plan_id: Optional[int] = None

    class Config:
        from_attributes = True

# Workout Plan schemas
class WorkoutPlanBase(BaseModel):
    name: str
    description: Optional[str] = None

class WorkoutPlanCreate(WorkoutPlanBase):
    exercises: List[ExerciseCreate]

class WorkoutPlan(WorkoutPlanBase):
    id: int
    trainer_id: Optional[int] = None
    exercises: List[Exercise] = []

    class Config:
        from_attributes = True

# Nutrition Plan schemas
class NutritionPlanBase(BaseModel):
    name: str
    description: Optional[str] = None

class NutritionPlanCreate(NutritionPlanBase):
    meals: List[MealCreate]

class NutritionPlan(NutritionPlanBase):
    id: int
    trainer_id: Optional[int] = None
    meals: List[Meal] = []

    class Config:
        from_attributes = True

# Routine schemas
class RoutineBase(BaseModel):
    name: str
    description: Optional[str] = None

class RoutineCreate(RoutineBase):
    exercises: List[ExerciseCreate]

class RoutineUpdate(RoutineBase):
    name: Optional[str] = None
    description: Optional[str] = None
    exercises: Optional[List[ExerciseCreate]] = None

class Routine(RoutineBase):
    id: int
    trainer_id: Optional[int] = None
    exercises: List[Exercise] = []

    class Config:
        from_attributes = True

# Progress tracking schemas
class UserMetricsBase(BaseModel):
    weight: Optional[float] = None
    body_fat: Optional[float] = None
    muscle_mass: Optional[float] = None
    height: Optional[float] = None
    bmi: Optional[float] = None
    notes: Optional[str] = None

class UserMetricsCreate(UserMetricsBase):
    pass

class UserMetrics(UserMetricsBase):
    id: int
    user_id: int
    date: date
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class WorkoutProgressBase(BaseModel):
    date: date
    completed: bool = False
    notes: Optional[str] = None

class WorkoutProgressCreate(WorkoutProgressBase):
    workout_plan_id: int

class WorkoutProgress(WorkoutProgressBase):
    id: int
    user_id: int
    workout_plan_id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class NutritionProgressBase(BaseModel):
    date: date
    completed: bool = False
    notes: Optional[str] = None

class NutritionProgressCreate(NutritionProgressBase):
    nutrition_plan_id: int

class NutritionProgress(NutritionProgressBase):
    id: int
    user_id: int
    nutrition_plan_id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# User schemas
class UserBase(BaseModel):
    email: str
    full_name: str
    height: Optional[float] = None
    target_weight: Optional[float] = None
    fitness_goal: Optional[str] = None
    health_conditions: Optional[str] = None
    emergency_contact: Optional[str] = None

class UserCreate(UserBase):
    password: str
    trainer_id: Optional[int] = None

class UserUpdate(UserBase):
    password: Optional[str] = None
    trainer_id: Optional[int] = None

class User(UserBase):
    id: int
    trainer_id: Optional[int] = None
    workout_plans: Optional[List[WorkoutPlan]] = []
    nutrition_plans: Optional[List[NutritionPlan]] = []
    metrics: Optional[List[UserMetrics]] = []
    workout_progress: Optional[List[WorkoutProgress]] = []
    nutrition_progress: Optional[List[NutritionProgress]] = []
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        from_attributes = True

# Trainer schemas
class TrainerBase(BaseModel):
    email: str
    full_name: str
    specialization: Optional[str] = None
    experience_years: Optional[int] = None
    certification: Optional[str] = None
    biography: Optional[str] = None

class TrainerCreate(TrainerBase):
    password: str

class TrainerUpdate(TrainerBase):
    password: Optional[str] = None

class Trainer(TrainerBase):
    id: int
    admin_id: int
    users: Optional[List[User]] = []
    workout_plans: Optional[List[WorkoutPlan]] = []
    nutrition_plans: Optional[List[NutritionPlan]] = []
    routines: Optional[List[Routine]] = []

    class Config:
        from_attributes = True

# Admin schemas
class AdminBase(BaseModel):
    email: EmailStr
    full_name: str

class AdminCreate(AdminBase):
    password: str

class AdminUpdate(AdminBase):
    password: Optional[str] = None

class Admin(AdminBase):
    id: int
    trainers: Optional[List[Trainer]] = []

    class Config:
        from_attributes = True

# Auth schemas
class Token(BaseModel):
    access_token: str
    token_type: str
    role: str

class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None

class AdminLoginReset(BaseModel):
    email: EmailStr

class PasswordReset(BaseModel):
    token: str
    new_password: str

# Response schemas
class ProgressReport(BaseModel):
    start_date: date
    end_date: date
    metrics: List[UserMetrics]
    workout_progress: List[WorkoutProgress]
    nutrition_progress: List[NutritionProgress]

class UserStats(BaseModel):
    total_workouts: int
    completed_workouts: int
    completion_rate: float
    initial_weight: Optional[float]
    current_weight: Optional[float]
    weight_change: Optional[float]
    initial_body_fat: Optional[float]
    current_body_fat: Optional[float]
    body_fat_change: Optional[float]

# Response model específico para los planes de usuario
class UserPlansResponse(BaseModel):
    workout_plans: List[WorkoutPlan]
    nutrition_plans: List[NutritionPlan]

    class Config:
        from_attributes = True