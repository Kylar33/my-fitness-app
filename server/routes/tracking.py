from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import date
from config.database import get_db
from models.tracking import ProgressTracking, WorkoutLog
from schemas.tracking import (
    ProgressTrackingCreate,
    ProgressTracking as ProgressTrackingSchema,
    WorkoutLogCreate,
    WorkoutLog as WorkoutLogSchema
)
from middleware.auth import get_current_trainer, get_current_user
from models.user import Trainer, User

router = APIRouter()

@router.post("/progress/", response_model=ProgressTrackingSchema)
async def create_progress_record(
    progress: ProgressTrackingCreate,
    db: Session = Depends(get_db),
    current_trainer = Depends(get_current_trainer)
):
    # Verificar que el usuario pertenece al entrenador
    user = db.query(User).filter(
        User.id == progress.user_id,
        User.trainer_id == current_trainer.id
    ).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db_progress = ProgressTracking(**progress.dict())
    db.add(db_progress)
    db.commit()
    db.refresh(db_progress)
    return db_progress

@router.post("/workout-log/", response_model=WorkoutLogSchema)
async def create_workout_log(
    log: WorkoutLogCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Los usuarios pueden registrar sus propios entrenamientos
    if isinstance(current_user, Trainer):
        user = db.query(User).filter(
            User.id == log.user_id,
            User.trainer_id == current_user.id
        ).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
    else:
        if current_user.id != log.user_id:
            raise HTTPException(
                status_code=403,
                detail="Not authorized to log workouts for other users"
            )

    db_log = WorkoutLog(**log.dict())
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

@router.get(
    "/progress/{user_id}",
    response_model=List[ProgressTrackingSchema]
)
async def get_user_progress(
    user_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Verificar permisos
    if isinstance(current_user, Trainer):
        if not db.query(User).filter(
            User.id == user_id,
            User.trainer_id == current_user.id
        ).first():
            raise HTTPException(
                status_code=403,
                detail="Not authorized to view this user's progress"
            )
    elif current_user.id != user_id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to view other user's progress"
        )

    progress = db.query(ProgressTracking).filter(
        ProgressTracking.user_id == user_id
    ).order_by(ProgressTracking.tracking_date.desc()).all()
    return progress