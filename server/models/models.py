from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String, Text, Table, Date, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from config.database import Base



user_workout_plans = Table(
    'user_workout_plans',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('workout_plan_id', Integer, ForeignKey('workout_plans.id'), primary_key=True)
)

user_nutrition_plans = Table(
    'user_nutrition_plans',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('nutrition_plan_id', Integer, ForeignKey('nutrition_plans.id'), primary_key=True)
)

class Admin(Base):
    __tablename__ = "admins"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255))
    full_name = Column(String(255))
    trainers = relationship("Trainer", back_populates="admin")

class Trainer(Base):
    __tablename__ = "trainers"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255))
    full_name = Column(String(255))
    specialization = Column(String(255))
    experience_years = Column(Integer)
    certification = Column(Text)
    biography = Column(Text)
    admin_id = Column(Integer, ForeignKey("admins.id"))
    
    admin = relationship("Admin", back_populates="trainers")
    users = relationship("User", back_populates="trainer")
    workout_plans = relationship("WorkoutPlan", back_populates="trainer")
    nutrition_plans = relationship("NutritionPlan", back_populates="trainer")
    routines = relationship("Routine", back_populates="trainer")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255))
    full_name = Column(String(255))
    height = Column(Float)
    target_weight = Column(Float)
    fitness_goal = Column(Text)
    health_conditions = Column(Text)
    emergency_contact = Column(String(255))
    trainer_id = Column(Integer, ForeignKey("trainers.id"))
    
    trainer = relationship("Trainer", back_populates="users")
    workout_plans = relationship("WorkoutPlan", secondary=user_workout_plans, back_populates="users")
    nutrition_plans = relationship("NutritionPlan", secondary=user_nutrition_plans, back_populates="users")
    metrics = relationship("UserMetrics", back_populates="user", cascade="all, delete")
    workout_progress = relationship("WorkoutProgress", back_populates="user", cascade="all, delete")
    nutrition_progress = relationship("NutritionProgress", back_populates="user", cascade="all, delete")

class WorkoutPlan(Base):
    __tablename__ = "workout_plans"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    trainer_id = Column(Integer, ForeignKey("trainers.id"))
    trainer = relationship("Trainer", back_populates="workout_plans")
    exercises = relationship("Exercise", back_populates="workout_plan", cascade="all, delete-orphan")
    users = relationship("User", secondary=user_workout_plans, back_populates="workout_plans")
    progress = relationship("WorkoutProgress", back_populates="workout_plan", cascade="all, delete")

class Exercise(Base):
    __tablename__ = "exercises"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    sets = Column(Integer, nullable=False)
    reps = Column(Integer, nullable=False)
    workout_plan_id = Column(Integer, ForeignKey("workout_plans.id"))
    routine_id = Column(Integer, ForeignKey("routines.id"))
    workout_plan = relationship("WorkoutPlan", back_populates="exercises")
    routine = relationship("Routine", back_populates="exercises")

class Routine(Base):
    __tablename__ = "routines"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    trainer_id = Column(Integer, ForeignKey("trainers.id"))
    trainer = relationship("Trainer", back_populates="routines")
    exercises = relationship("Exercise", back_populates="routine")

class NutritionPlan(Base):
    __tablename__ = "nutrition_plans"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    trainer_id = Column(Integer, ForeignKey("trainers.id"))
    trainer = relationship("Trainer", back_populates="nutrition_plans")
    meals = relationship("Meal", back_populates="nutrition_plan", cascade="all, delete-orphan")
    users = relationship("User", secondary=user_nutrition_plans, back_populates="nutrition_plans")
    progress = relationship("NutritionProgress", back_populates="nutrition_plan", cascade="all, delete")

class Meal(Base):
    __tablename__ = "meals"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    calories = Column(Integer, nullable=False)
    nutrition_plan_id = Column(Integer, ForeignKey("nutrition_plans.id"))
    nutrition_plan = relationship("NutritionPlan", back_populates="meals")

class UserMetrics(Base):
    __tablename__ = "user_metrics"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    date = Column(Date, nullable=False)
    weight = Column(Float)
    body_fat = Column(Float)
    muscle_mass = Column(Float)
    height = Column(Float)
    bmi = Column(Float)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="metrics")

class WorkoutProgress(Base):
    __tablename__ = "workout_progress"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    workout_plan_id = Column(Integer, ForeignKey("workout_plans.id", ondelete="CASCADE"))
    date = Column(Date, nullable=False)
    completed = Column(Boolean, default=False)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="workout_progress")
    workout_plan = relationship("WorkoutPlan", back_populates="progress")

class NutritionProgress(Base):
    __tablename__ = "nutrition_progress"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    nutrition_plan_id = Column(Integer, ForeignKey("nutrition_plans.id", ondelete="CASCADE"))
    date = Column(Date, nullable=False)
    completed = Column(Boolean, default=False)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="nutrition_progress")
    nutrition_plan = relationship("NutritionPlan", back_populates="progress")

