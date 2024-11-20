from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import date
from config.database import get_db
import models.models as models
import schemas.schemas as schemas
from utils.auth import get_current_user, get_current_trainer

router = APIRouter(prefix="/progress", tags=["progress"])

@router.post("/workout", response_model=schemas.WorkoutProgress)
async def record_workout_progress(
    progress: schemas.WorkoutProgressCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    
    workout_plan = db.query(models.WorkoutPlan).filter(
        models.WorkoutPlan.i)
    
    workout_plan = db.query(models.WorkoutPlan).filter(
        models.WorkoutPlan.id == progress.workout_plan_id
    ).first()
    
    if not workout_plan:
        raise HTTPException(status_code=404, detail="Plan de entrenamiento no encontrado")
    
    
    if workout_plan.id not in [p.id for p in current_user["user"].workout_plans]:
        raise HTTPException(status_code=403, detail="No tienes acceso a este plan")
    
    
    db_progress = models.WorkoutProgress(
        user_id=current_user["user"].id,
        **progress.dict()
    )
    db.add(db_progress)
    db.commit()
    db.refresh(db_progress)
    return db_progress

@router.post("/nutrition", response_model=schemas.NutritionProgress)
async def record_nutrition_progress(
    progress: schemas.NutritionProgressCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    
    nutrition_plan = db.query(models.NutritionPlan).filter(
        models.NutritionPlan.id == progress.nutrition_plan_id
    ).first()
    
    if not nutrition_plan:
        raise HTTPException(status_code=404, detail="Plan nutricional no encontrado")
    
   
    if nutrition_plan.id not in [p.id for p in current_user["user"].nutrition_plans]:
        raise HTTPException(status_code=403, detail="No tienes acceso a este plan")
    
    
    db_progress = models.NutritionProgress(
        user_id=current_user["user"].id,
        **progress.dict()
    )
    db.add(db_progress)
    db.commit()
    db.refresh(db_progress)
    return db_progress

@router.get("/workout/{plan_id}", response_model=List[schemas.WorkoutProgress])
async def get_workout_progress(
    plan_id: int,
    start_date: date = None,
    end_date: date = None,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(models.WorkoutProgress).filter(
        models.WorkoutProgress.workout_plan_id == plan_id,
        models.WorkoutProgress.user_id == current_user["user"].id
    )
    
    if start_date:
        query = query.filter(models.WorkoutProgress.date >= start_date)
    if end_date:
        query = query.filter(models.WorkoutProgress.date <= end_date)
    
    return query.order_by(models.WorkoutProgress.date.desc()).all()

@router.get("/nutrition/{plan_id}", response_model=List[schemas.NutritionProgress])
async def get_nutrition_progress(
    plan_id: int,
    start_date: date = None,
    end_date: date = None,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(models.NutritionProgress).filter(
        models.NutritionProgress.nutrition_plan_id == plan_id,
        models.NutritionProgress.user_id == current_user["user"].id
    )
    
    if start_date:
        query = query.filter(models.NutritionProgress.date >= start_date)
    if end_date:
        query = query.filter(models.NutritionProgress.date <= end_date)
    
    return query.order_by(models.NutritionProgress.date.desc()).all()

@router.get("/trainer/users/{user_id}/workout", response_model=List[schemas.WorkoutProgress])
async def get_user_workout_progress(
    user_id: int,
    plan_id: int = None,
    start_date: date = None,
    end_date: date = None,
    current_user = Depends(get_current_trainer),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(
        models.User.id == user_id,
        models.User.trainer_id == current_user["user"].id
    ).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    query = db.query(models.WorkoutProgress).filter(
        models.WorkoutProgress.user_id == user_id
    )
    
    if plan_id:
        query = query.filter(models.WorkoutProgress.workout_plan_id == plan_id)
    if start_date:
        query = query.filter(models.WorkoutProgress.date >= start_date)
    if end_date:
        query = query.filter(models.WorkoutProgress.date <= end_date)
    
    return query.order_by(models.WorkoutProgress.date.desc()).all()

@router.get("/trainer/users/{user_id}/nutrition", response_model=List[schemas.NutritionProgress])
async def get_user_nutrition_progress(
    user_id: int,
    plan_id: int = None,
    start_date: date = None,
    end_date: date = None,
    current_user = Depends(get_current_trainer),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(
        models.User.id == user_id,
        models.User.trainer_id == current_user["user"].id
    ).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    query = db.query(models.NutritionProgress).filter(
        models.NutritionProgress.user_id == user_id
    )
    
    if plan_id:
        query = query.filter(models.NutritionProgress.nutrition_plan_id == plan_id)
    if start_date:
        query = query.filter(models.NutritionProgress.date >= start_date)
    if end_date:
        query = query.filter(models.NutritionProgress.date <= end_date)
    
    return query.order_by(models.NutritionProgress.date.desc()).all()