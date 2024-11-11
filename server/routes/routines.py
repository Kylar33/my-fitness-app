from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from config.database import get_db
from models.routine import Routine, Exercise
from schemas.routine import RoutineCreate, Routine as RoutineSchema
from middleware.auth import get_current_trainer

router = APIRouter()

@router.post("/routines/", response_model=RoutineSchema)
async def create_routine(
    routine: RoutineCreate,
    db: Session = Depends(get_db),
    current_trainer = Depends(get_current_trainer)
):
    db_routine = Routine(
        name=routine.name,
        description=routine.description,
        trainer_id=current_trainer.id
    )
    db.add(db_routine)
    db.commit()
    db.refresh(db_routine)

    for exercise in routine.exercises:
        db_exercise = Exercise(
            **exercise.dict(),
            routine_id=db_routine.id
        )
        db.add(db_exercise)
    
    db.commit()
    db.refresh(db_routine)
    return db_routine

@router.get("/routines/", response_model=List[RoutineSchema])
async def read_routines(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_trainer = Depends(get_current_trainer)
):
    routines = db.query(Routine).filter(
        Routine.trainer_id == current_trainer.id
    ).offset(skip).limit(limit).all()
    return routines

@router.get("/routines/{routine_id}", response_model=RoutineSchema)
async def read_routine(
    routine_id: int,
    db: Session = Depends(get_db),
    current_trainer = Depends(get_current_trainer)
):
    routine = db.query(Routine).filter(
        Routine.id == routine_id,
        Routine.trainer_id == current_trainer.id
    ).first()
    if routine is None:
        raise HTTPException(status_code=404, detail="Routine not found")
    return routine