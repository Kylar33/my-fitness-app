from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import Integer, func
import models.models as models

def calculate_bmi(weight: float, height: float) -> float:
    """Calculate BMI given weight in kg and height in meters"""
    return weight / (height * height)

def calculate_progress_stats(metrics: List[models.UserMetrics]):
    """Calculate progress statistics from a list of metrics"""
    if not metrics:
        return None
    
    sorted_metrics = sorted(metrics, key=lambda x: x.date)
    initial = sorted_metrics[0]
    current = sorted_metrics[-1]
    
    return {
        "initial_weight": initial.weight,
        "current_weight": current.weight,
        "weight_change": round(current.weight - initial.weight, 2) if initial.weight and current.weight else None,
        "initial_body_fat": initial.body_fat,
        "current_body_fat": current.body_fat,
        "body_fat_change": round(current.body_fat - initial.body_fat, 2) if initial.body_fat and current.body_fat else None,
        "initial_date": initial.date,
        "current_date": current.date,
        "days_tracked": (current.date - initial.date).days
    }

def get_user_completion_rates(db: Session, user_id: int, start_date: datetime, end_date: datetime):
    """Calculate completion rates for workout and nutrition plans"""
    workout_stats = db.query(
        func.count(models.WorkoutProgress.id).label('total'),
        func.sum(models.WorkoutProgress.completed.cast(Integer)).label('completed')
    ).filter(
        models.WorkoutProgress.user_id == user_id,
        models.WorkoutProgress.date.between(start_date, end_date)
    ).first()

    nutrition_stats = db.query(
        func.count(models.NutritionProgress.id).label('total'),
        func.sum(models.NutritionProgress.completed.cast(Integer)).label('completed')
    ).filter(
        models.NutritionProgress.user_id == user_id,
        models.NutritionProgress.date.between(start_date, end_date)
    ).first()

    return {
        "workout": {
            "total": workout_stats.total or 0,
            "completed": workout_stats.completed or 0,
            "rate": round(workout_stats.completed / workout_stats.total * 100, 2) if workout_stats.total else 0
        },
        "nutrition": {
            "total": nutrition_stats.total or 0,
            "completed": nutrition_stats.completed or 0,
            "rate": round(nutrition_stats.completed / nutrition_stats.total * 100, 2) if nutrition_stats.total else 0
        }
    }