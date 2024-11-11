
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from config.database import Base

class UserRoutine(Base):
    __tablename__ = "user_routines"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    routine_id = Column(Integer, ForeignKey("routines.id"))
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", backref="routines")
    routine = relationship("Routine")

class UserNutritionPlan(Base):
    __tablename__ = "user_nutrition_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    nutrition_plan_id = Column(Integer, ForeignKey("nutrition_plans.id"))
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", backref="nutrition_plans")
    nutrition_plan = relationship("NutritionPlan")