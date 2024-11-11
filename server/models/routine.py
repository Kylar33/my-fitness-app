from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from config.database import Base

class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    sets = Column(Integer)
    reps = Column(Integer)
    rest_time = Column(Integer)  # en segundos
    routine_id = Column(Integer, ForeignKey("routines.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    routine = relationship("Routine", back_populates="exercises")

class Routine(Base):
    __tablename__ = "routines"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    trainer_id = Column(Integer, ForeignKey("trainers.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    exercises = relationship("Exercise", back_populates="routine")