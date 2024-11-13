# routes/user_panel.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict
from datetime import date, timedelta
from config.database import get_db
from models.tracking import ProgressTracking, WorkoutLog
from models.assignments import UserRoutine, UserNutritionPlan
from middleware.auth import get_current_user
from models.user import Trainer

router = APIRouter()

@router.get("/my-dashboard/")
async def get_user_dashboard(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if isinstance(current_user, Trainer):
        raise HTTPException(
            status_code=403,
            detail="This endpoint is only for regular users"
        )

    # Obtener rutinas activas
    active_routines = db.query(UserRoutine).filter(
        UserRoutine.user_id == current_user.id,
        UserRoutine.end_date >= date.today()
    ).all()

    # Obtener planes nutricionales activos
    active_nutrition_plans = db.query(UserNutritionPlan).filter(
        UserNutritionPlan.user_id == current_user.id,
        UserNutritionPlan.end_date >= date.today()
    ).all()

    # Obtener último seguimiento
    last_progress = db.query(ProgressTracking).filter(
        ProgressTracking.user_id == current_user.id
    ).order_by(ProgressTracking.tracking_date.desc()).first()

    # Obtener registros de ejercicio recientes
    recent_workouts = db.query(WorkoutLog).filter(
        WorkoutLog.user_id == current_user.id,
        WorkoutLog.workout_date >= date.today() - timedelta(days=7)
    ).order_by(WorkoutLog.workout_date.desc()).all()

    return {
        "active_routines": active_routines,
        "active_nutrition_plans": active_nutrition_plans,
        "last_progress": last_progress,
        "recent_workouts": recent_workouts
    }

@router.get("/my-progress/")
async def get_user_progress_summary(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if isinstance(current_user, Trainer):
        raise HTTPException(
            status_code=403,
            detail="This endpoint is only for regular users"
        )

    # Obtener historial de progreso
    progress_history = db.query(ProgressTracking).filter(
        ProgressTracking.user_id == current_user.id
    ).order_by(ProgressTracking.tracking_date.desc()).all()

    # Calcular cambios
    if len(progress_history) >= 2:
        weight_change = progress_history[0].weight - progress_history[-1].weight
        body_fat_change = None
        if progress_history[0].body_fat and progress_history[-1].body_fat:
            body_fat_change = progress_history[0].body_fat - progress_history[-1].body_fat
    else:
        weight_change = 0
        body_fat_change = None

    return {
        "current_stats": progress_history[0] if progress_history else None,
        "weight_change": weight_change,
        "body_fat_change": body_fat_change,
        "progress_history": progress_history
    }

@router.get("/my-workout-history/")
async def get_workout_history(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if isinstance(current_user, Trainer):
        raise HTTPException(
            status_code=403,
            detail="This endpoint is only for regular users"
        )

    # Obtener historial de ejercicios
    workout_history = db.query(WorkoutLog).filter(
        WorkoutLog.user_id == current_user.id
    ).order_by(WorkoutLog.workout_date.desc()).all()

    return workout_history