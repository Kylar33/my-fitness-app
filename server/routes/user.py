from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from config.database import get_db
import models.models as models
import schemas.schemas as schemas
from utils.auth import get_current_user

router = APIRouter(prefix="/user", tags=["user"])

@router.get("/profile/", response_model=schemas.User)
def read_user_profile(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user["role"] != "user":
        raise HTTPException(status_code=403, detail="Only users can access their profile")
    return current_user["user"]

@router.put("/profile/", response_model=schemas.User)
def update_user_profile(
    user_update: schemas.UserUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user["role"] != "user":
        raise HTTPException(status_code=403, detail="Only users can update their profile")
    
    user = db.query(models.User).filter(models.User.id == current_user["user"].id).first()
    
    for field, value in user_update.dict(exclude_unset=True).items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    return user

@router.get("/plans/", response_model=dict)
async def get_user_plans(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user["role"] != "user":
        raise HTTPException(status_code=403, detail="Only users can access their plans")
    
    user = db.query(models.User).filter(models.User.id == current_user["user"].id).first()
    
    return {
        "workout_plans": [
            {
                "id": plan.id,
                "name": plan.name,
                "description": plan.description,
                "exercises": [
                    {
                        "name": exercise.name,
                        "sets": exercise.sets,
                        "reps": exercise.reps
                    } for exercise in plan.exercises
                ]
            } for plan in user.workout_plans
        ],
        "nutrition_plans": [
            {
                "id": plan.id,
                "name": plan.name,
                "description": plan.description,
                "meals": [
                    {
                        "name": meal.name,
                        "description": meal.description,
                        "calories": meal.calories
                    } for meal in plan.meals
                ]
            } for plan in user.nutrition_plans
        ]
    }

@router.get("/progress/", response_model=dict)
async def get_user_progress(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user["role"] != "user":
        raise HTTPException(status_code=403, detail="Only users can access their progress")
    
    user = db.query(models.User).filter(models.User.id == current_user["user"].id).first()
    
    return {
        "workout_progress": user.workout_progress,
        "nutrition_progress": user.nutrition_progress,
        "metrics": user.metrics
    }

@router.get("/progress/stats")
async def get_user_progress_stats(
    range: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user["role"] != "user":
        raise HTTPException(status_code=403, detail="Only users can access their stats")
    
    user = db.query(models.User).filter(models.User.id == current_user["user"].id).first()
    
    # Get stats based on range (month in this case)
    if range == "month":
        return {
            "workout_stats": {
                "completed_workouts": len([wp for wp in user.workout_progress if wp.completed]),
                "total_workouts": len(user.workout_progress)
            },
            "nutrition_stats": {
                "adherence_rate": len([np for np in user.nutrition_progress if np.completed]) / len(user.nutrition_progress) if user.nutrition_progress else 0
            },
            "metrics_progress": {
                "weight": [metric.weight for metric in user.metrics],
                "body_fat": [metric.body_fat for metric in user.metrics],
                "muscle_mass": [metric.muscle_mass for metric in user.metrics]
            }
        }
    
    raise HTTPException(status_code=400, detail="Invalid range parameter")

@router.get("/goals/")
async def get_user_goals(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user["role"] != "user":
        raise HTTPException(status_code=403, detail="Only users can access their goals")
    
    user = db.query(models.User).filter(models.User.id == current_user["user"].id).first()
    
    return {
        "fitness_goal": user.fitness_goal,
        "weight_goal": user.weight_goal,
        "body_fat_goal": user.body_fat_goal,
        "muscle_mass_goal": user.muscle_mass_goal,
        "goal_target_date": user.goal_target_date
    }
