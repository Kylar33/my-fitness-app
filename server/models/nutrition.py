from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from config.database import Base

class Meal(Base):
    __tablename__ = "meals"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    calories = Column(Float)
    protein = Column(Float)
    carbs = Column(Float)
    fats = Column(Float)
    time_of_day = Column(String)  # breakfast, lunch, dinner, snack
    nutrition_plan_id = Column(Integer, ForeignKey("nutrition_plans.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    nutrition_plan = relationship("NutritionPlan", back_populates="meals")

class NutritionPlan(Base):
    __tablename__ = "nutrition_plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    trainer_id = Column(Integer, ForeignKey("trainers.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    meals = relationship("Meal", back_populates="nutrition_plan")