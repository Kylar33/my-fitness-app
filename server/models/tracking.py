from sqlalchemy import Column, Integer, Float, Text, ForeignKey, DateTime, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from config.database import Base

class ProgressTracking(Base):
    __tablename__ = "progress_tracking"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    weight = Column(Float)
    height = Column(Float)
    body_fat = Column(Float, nullable=True)
    muscle_mass = Column(Float, nullable=True)
    notes = Column(Text)
    tracking_date = Column(Date, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", backref="progress_records")

class WorkoutLog(Base):
    __tablename__ = "workout_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    routine_id = Column(Integer, ForeignKey("routines.id"))
    exercise_id = Column(Integer, ForeignKey("exercises.id"))
    sets_completed = Column(Integer)
    reps_completed = Column(Integer)
    weight_used = Column(Float)
    notes = Column(Text)
    workout_date = Column(Date, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())