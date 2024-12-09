from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, Integer
from typing import List
from datetime import date, datetime, timedelta
from config.database import get_db
import models.models as models
import schemas.schemas as schemas
from utils.auth import get_current_trainer, get_password_hash
from utils.metrics import calculate_progress_stats, get_user_completion_rates

router = APIRouter(prefix="/trainer", tags=["trainer"])

# Users Management
@router.post("/users/", response_model=schemas.User)
def create_user(
    user: schemas.UserCreate,
    current_user = Depends(get_current_trainer),
    db: Session = Depends(get_db)
):
    # Verificar si el email ya existe
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email ya registrado"
        )

    db_user = models.User(
        email=user.email,
        hashed_password=get_password_hash(user.password),
        full_name=user.full_name,
        trainer_id=current_user["user"].id,
        height=user.height,
        target_weight=user.target_weight,
        fitness_goal=user.fitness_goal,
        health_conditions=user.health_conditions,
        emergency_contact=user.emergency_contact
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/users/", response_model=List[schemas.User])
def read_users(
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_trainer),
    db: Session = Depends(get_db)
):
    users = db.query(models.User).filter(
        models.User.trainer_id == current_user["user"].id
    ).offset(skip).limit(limit).all()
    return users

@router.get("/users/{user_id}", response_model=schemas.User)
def read_user(
    user_id: int,
    current_user = Depends(get_current_trainer),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(
        models.User.id == user_id,
        models.User.trainer_id == current_user["user"].id
    ).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user

@router.put("/users/{user_id}", response_model=schemas.User)
def update_user(
    user_id: int,
    user_update: schemas.UserUpdate,
    current_user = Depends(get_current_trainer),
    db: Session = Depends(get_db)
):
    db_user = db.query(models.User).filter(
        models.User.id == user_id,
        models.User.trainer_id == current_user["user"].id
    ).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    if user_update.email != db_user.email:
        existing_user = db.query(models.User).filter(
            models.User.email == user_update.email,
            models.User.id != user_id
        ).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email ya está en uso")

    for key, value in user_update.dict(exclude_unset=True).items():
        if key == "password" and value:
            setattr(db_user, "hashed_password", get_password_hash(value))
        else:
            setattr(db_user, key, value)

    try:
        db.commit()
        db.refresh(db_user)
        return db_user
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    current_user = Depends(get_current_trainer),
    db: Session = Depends(get_db)
):
    db_user = db.query(models.User).filter(
        models.User.id == user_id,
        models.User.trainer_id == current_user["user"].id
    ).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    db.delete(db_user)
    db.commit()
    return {"message": "Usuario eliminado exitosamente"}

@router.get("/users/{user_id}/workout-plans/", response_model=List[schemas.WorkoutPlan])
def read_user_workout_plans(
        user_id: int,
        current_user = Depends(get_current_trainer),
        db: Session = Depends(get_db)
    ):
        db_user = db.query(models.User).filter(
            models.User.id == user_id,
            models.User.trainer_id == current_user["user"].id
        ).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        # Return the workout plans through the relationship
        return db_user.workout_plans


@router.get("/users/{user_id}/nutritional-plans/", response_model=List[schemas.NutritionPlan])
def read_user_nutritional_plans(
        user_id: int,
        current_user = Depends(get_current_trainer),
        db: Session = Depends(get_db)
    ):
        db_user = db.query(models.User).filter(
            models.User.id == user_id,
            models.User.trainer_id == current_user["user"].id
        ).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        # Return the nutritional plans through the relationship
        return db_user.nutrition_plans

@router.get("/metrics/user/{user_id}/metrics")
def get_user_metrics(
    user_id: int,
    current_user = Depends(get_current_trainer),
    db: Session = Depends(get_db)
):
    db_user = db.query(models.User).filter(
        models.User.id == user_id,
        models.User.trainer_id == current_user["user"].id
    ).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Assuming there is a method to get metrics for the user
    metrics = db_user.get_metrics()  # This method should be defined in the User model
    return metrics



# Workout Plans Management
@router.get("/workout-plans/", response_model=List[schemas.WorkoutPlan])
def read_workout_plans(
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_trainer),
    db: Session = Depends(get_db)
):
    workout_plans = db.query(models.WorkoutPlan).filter(
        models.WorkoutPlan.trainer_id == current_user["user"].id
    ).options(joinedload(models.WorkoutPlan.exercises))\
    .offset(skip).limit(limit).all()
    return workout_plans

@router.post("/workout-plans/", response_model=schemas.WorkoutPlan)
def create_workout_plan(
    plan: schemas.WorkoutPlanCreate,
    current_user = Depends(get_current_trainer),
    db: Session = Depends(get_db)
):
    db_plan = models.WorkoutPlan(
        name=plan.name,
        description=plan.description,
        trainer_id=current_user["user"].id
    )
    db.add(db_plan)
    db.flush()

    for exercise in plan.exercises:
        db_exercise = models.Exercise(
            **exercise.dict(),
            workout_plan_id=db_plan.id
        )
        db.add(db_exercise)

    db.commit()
    db.refresh(db_plan)
    return db_plan

@router.get("/workout-plans/{plan_id}", response_model=schemas.WorkoutPlan)
def read_workout_plan(
    plan_id: int,
    current_user = Depends(get_current_trainer),
    db: Session = Depends(get_db)
):
    plan = db.query(models.WorkoutPlan).filter(
        models.WorkoutPlan.id == plan_id,
        models.WorkoutPlan.trainer_id == current_user["user"].id
    ).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan no encontrado")
    return plan

@router.put("/workout-plans/{plan_id}", response_model=schemas.WorkoutPlan)
def update_workout_plan(
    plan_id: int,
    plan_update: schemas.WorkoutPlanCreate,
    current_user = Depends(get_current_trainer),
    db: Session = Depends(get_db)
):
    db_plan = db.query(models.WorkoutPlan).filter(
        models.WorkoutPlan.id == plan_id,
        models.WorkoutPlan.trainer_id == current_user["user"].id
    ).first()
    if not db_plan:
        raise HTTPException(status_code=404, detail="Plan no encontrado")
    
    db_plan.name = plan_update.name
    db_plan.description = plan_update.description
    
    # Delete existing exercises
    db.query(models.Exercise).filter(models.Exercise.workout_plan_id == plan_id).delete()
    
    # Add new exercises
    for exercise in plan_update.exercises:
        db_exercise = models.Exercise(
            **exercise.dict(),
            workout_plan_id=db_plan.id
        )
        db.add(db_exercise)
    
    try:
        db.commit()
        db.refresh(db_plan)
        return db_plan
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/workout-plans/{plan_id}")
def delete_workout_plan(
    plan_id: int,
    current_user = Depends(get_current_trainer),
    db: Session = Depends(get_db)
):
    db_plan = db.query(models.WorkoutPlan).filter(
        models.WorkoutPlan.id == plan_id,
        models.WorkoutPlan.trainer_id == current_user["user"].id
    ).first()
    if not db_plan:
        raise HTTPException(status_code=404, detail="Plan no encontrado")
    
    db.delete(db_plan)
    db.commit()
    return {"message": "Plan eliminado exitosamente"}

# Nutrition Plans Management
@router.post("/nutrition-plans/", response_model=schemas.NutritionPlan)
def create_nutrition_plan(
    plan: schemas.NutritionPlanCreate,
    current_user = Depends(get_current_trainer),
    db: Session = Depends(get_db)
):
    db_plan = models.NutritionPlan(
        name=plan.name,
        description=plan.description,
        trainer_id=current_user["user"].id
    )
    db.add(db_plan)
    db.flush()

    for meal in plan.meals:
        db_meal = models.Meal(
            **meal.dict(),
            nutrition_plan_id=db_plan.id
        )
        db.add(db_meal)

    db.commit()
    db.refresh(db_plan)
    return db_plan

@router.get("/nutrition-plans/", response_model=List[schemas.NutritionPlan])
def read_nutrition_plans(
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_trainer),
    db: Session = Depends(get_db)
):
    plans = db.query(models.NutritionPlan).filter(
        models.NutritionPlan.trainer_id == current_user["user"].id
    ).options(joinedload(models.NutritionPlan.meals))\
    .offset(skip).limit(limit).all()
    return plans

@router.get("/nutrition-plans/{plan_id}", response_model=schemas.NutritionPlan)
def read_nutrition_plan(
    plan_id: int,
    current_user = Depends(get_current_trainer),
    db: Session = Depends(get_db)
):
    plan = db.query(models.NutritionPlan).filter(
        models.NutritionPlan.id == plan_id,
        models.NutritionPlan.trainer_id == current_user["user"].id
    ).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan no encontrado")
    return plan

@router.put("/nutrition-plans/{plan_id}", response_model=schemas.NutritionPlan)
def update_nutrition_plan(
    plan_id: int,
    plan_update: schemas.NutritionPlanCreate,
    current_user = Depends(get_current_trainer),
    db: Session = Depends(get_db)
):
    db_plan = db.query(models.NutritionPlan).filter(
        models.NutritionPlan.id == plan_id,
        models.NutritionPlan.trainer_id == current_user["user"].id
    ).first()
    if not db_plan:
        raise HTTPException(status_code=404, detail="Plan no encontrado")
    
    db_plan.name = plan_update.name
    db_plan.description = plan_update.description
    
    # Delete existing meals
    db.query(models.Meal).filter(models.Meal.nutrition_plan_id == plan_id).delete()
    
    # Add new meals
    for meal in plan_update.meals:
        db_meal = models.Meal(
            **meal.dict(),
            nutrition_plan_id=db_plan.id
        )
        db.add(db_meal)
    
    try:
        db.commit()
        db.refresh(db_plan)
        return db_plan
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/nutrition-plans/{plan_id}")
def delete_nutrition_plan(
    plan_id: int,
    current_user = Depends(get_current_trainer),
    db: Session = Depends(get_db)
):
    db_plan = db.query(models.NutritionPlan).filter(
        models.NutritionPlan.id == plan_id,
        models.NutritionPlan.trainer_id == current_user["user"].id
    ).first()
    if not db_plan:
        raise HTTPException(status_code=404, detail="Plan no encontrado")
    
    db.delete(db_plan)
    db.commit()
    return {"message": "Plan eliminado exitosamente"}

# Progress Tracking
@router.get("/users/{user_id}/progress", response_model=schemas.ProgressReport)
async def get_user_progress(
    user_id: int,
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
    
    if not start_date:
        start_date = datetime.utcnow() - timedelta(days=30)
    if not end_date:
        end_date = datetime.utcnow()

    metrics = db.query(models.UserMetrics).filter(
        models.UserMetrics.user_id == user_id,
        models.UserMetrics.date.between(start_date, end_date)
    ).order_by(models.UserMetrics.date).all()

    workout_progress = db.query(models.WorkoutProgress).filter(
        models.WorkoutProgress.user_id == user_id,
        models.WorkoutProgress.date.between(start_date, end_date)
    ).order_by(models.WorkoutProgress.date).all()

    nutrition_progress = db.query(models.NutritionProgress).filter(
        models.NutritionProgress.user_id == user_id,
        models.NutritionProgress.date.between(start_date, end_date)
    ).order_by(models.NutritionProgress.date).all()

    return {
        "start_date": start_date,
        "end_date": end_date,
        "metrics": metrics,
        "workout_progress": workout_progress,
        "nutrition_progress": nutrition_progress
    }

# Dashboard
@router.get("/dashboard/stats")
async def get_trainer_stats(
    current_user = Depends(get_current_trainer),
    db: Session = Depends(get_db)
):
    trainer_id = current_user["user"].id
    
    total_users = db.query(models.User).filter(
        models.User.trainer_id == trainer_id
    ).count()
    
    total_workout_plans = db.query(models.WorkoutPlan).filter(
        models.WorkoutPlan.trainer_id == trainer_id
    ).count()
    
    total_nutrition_plans = db.query(models.NutritionPlan).filter(
        models.NutritionPlan.trainer_id == trainer_id
    ).count()
    
    # Estadísticas de los últimos 30 días
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    # Usuarios activos (que han registrado progreso en los últimos 30 días)
    active_users = db.query(models.User).join(models.WorkoutProgress).filter(
        models.User.trainer_id == trainer_id,
        models.WorkoutProgress.date >= thirty_days_ago
    ).distinct().count()
    
    # Promedio de cumplimiento de planes
    workout_completion = db.query(
        models.WorkoutProgress
    ).join(
        models.User
    ).filter(
        models.User.trainer_id == trainer_id,
        models.WorkoutProgress.date >= thirty_days_ago
    ).with_entities(
        func.avg(models.WorkoutProgress.completed.cast(Integer)) * 100    ).scalar() or 0

    nutrition_completion = db.query(
        models.NutritionProgress
    ).join(
        models.User
    ).filter(
        models.User.trainer_id == trainer_id,
        models.NutritionProgress.date >= thirty_days_ago
    ).with_entities(
        func.avg(models.NutritionProgress.completed.cast(Integer)) * 100    ).scalar() or 0

    return {
        "total_stats": {
            "users": total_users,
            "workout_plans": total_workout_plans,
            "nutrition_plans": total_nutrition_plans,
            "active_users": active_users
        },
        "completion_rates": {
            "workout": round(workout_completion, 2),
            "nutrition": round(nutrition_completion, 2)
        }
    }

# Asignación de planes
@router.post("/assign-workout/{user_id}/{plan_id}")
async def assign_workout_plan(
    user_id: int,
    plan_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_trainer)
):
    # Verificar si el usuario existe y pertenece al entrenador
    user = db.query(models.User).filter(
        models.User.id == user_id,
        models.User.trainer_id == current_user["user"].id
    ).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Verificar si el plan existe y pertenece al entrenador
    plan = db.query(models.WorkoutPlan).filter(
        models.WorkoutPlan.id == plan_id,
        models.WorkoutPlan.trainer_id == current_user["user"].id
    ).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan no encontrado")

    # Verificar si ya existe la asignación
    if plan in user.workout_plans:
        raise HTTPException(status_code=400, detail="El plan ya está asignado a este usuario")

    # Realizar la asignación
    user.workout_plans.append(plan)
    try:
        db.commit()
        return {"message": "Plan asignado exitosamente"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/assign-nutrition/{user_id}/{plan_id}")
async def assign_nutrition_plan(
    user_id: int,
    plan_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_trainer)
):
    # Verificar si el usuario existe y pertenece al entrenador
    user = db.query(models.User).filter(
        models.User.id == user_id,
        models.User.trainer_id == current_user["user"].id
    ).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Verificar si el plan existe y pertenece al entrenador
    plan = db.query(models.NutritionPlan).filter(
        models.NutritionPlan.id == plan_id,
        models.NutritionPlan.trainer_id == current_user["user"].id
    ).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan no encontrado")

    # Verificar si ya existe la asignación
    if plan in user.nutrition_plans:
        raise HTTPException(status_code=400, detail="El plan ya está asignado a este usuario")

    # Realizar la asignación
    user.nutrition_plans.append(plan)
    try:
        db.commit()
        return {"message": "Plan nutricional asignado exitosamente"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))



@router.delete("/unassign-workout/{user_id}/{plan_id}")
async def unassign_workout_plan(
    user_id: int,
    plan_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_trainer)
):
    # Verificar si el usuario existe y pertenece al entrenador
    user = db.query(models.User).filter(
        models.User.id == user_id,
        models.User.trainer_id == current_user["user"].id
    ).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Verificar si el plan existe y está asignado
    plan = db.query(models.WorkoutPlan).filter(
        models.WorkoutPlan.id == plan_id,
        models.WorkoutPlan.trainer_id == current_user["user"].id
    ).first()
    if not plan or plan not in user.workout_plans:
        raise HTTPException(status_code=404, detail="Plan no encontrado o no asignado")

    # Remover la asignación
    user.workout_plans.remove(plan)
    try:
        db.commit()
        return {"message": "Plan removido exitosamente"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/unassign-nutrition/{user_id}/{plan_id}")
async def unassign_nutrition_plan(
    user_id: int,
    plan_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_trainer)
):
    # Verificar si el usuario existe y pertenece al entrenador
    user = db.query(models.User).filter(
        models.User.id == user_id,
        models.User.trainer_id == current_user["user"].id
    ).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Verificar si el plan existe y está asignado
    plan = db.query(models.NutritionPlan).filter(
        models.NutritionPlan.id == plan_id,
        models.NutritionPlan.trainer_id == current_user["user"].id
    ).first()
    if not plan or plan not in user.nutrition_plans:
        raise HTTPException(status_code=404, detail="Plan no encontrado o no asignado")

    # Remover la asignación
    user.nutrition_plans.remove(plan)
    try:
        db.commit()
        return {"message": "Plan nutricional removido exitosamente"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user-stats/{user_id}")
async def get_user_statistics(
    user_id: int,
    period: str = "month",  # "week", "month", "year"
    db: Session = Depends(get_db),
    current_user = Depends(get_current_trainer)
):
    # Verificar si el usuario existe y pertenece al entrenador
    user = db.query(models.User).filter(
        models.User.id == user_id,
        models.User.trainer_id == current_user["user"].id
    ).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Determinar el rango de fechas
    end_date = datetime.utcnow()
    if period == "week":
        start_date = end_date - timedelta(days=7)
    elif period == "month":
        start_date = end_date - timedelta(days=30)
    elif period == "year":
        start_date = end_date - timedelta(days=365)
    else:
        raise HTTPException(status_code=400, detail="Período inválido")

    # Obtener métricas
    metrics = db.query(models.UserMetrics).filter(
        models.UserMetrics.user_id == user_id,
        models.UserMetrics.date.between(start_date, end_date)
    ).all()

    # Calcular estadísticas
    completion_rates = get_user_completion_rates(db, user_id, start_date, end_date)
    progress_stats = calculate_progress_stats(metrics) if metrics else None

    return {
        "period": period,
        "start_date": start_date,
        "end_date": end_date,
        "completion_rates": completion_rates,
        "progress_stats": progress_stats,
        "total_workout_plans": len(user.workout_plans),
        "total_nutrition_plans": len(user.nutrition_plans)
    }

@router.get("/user/goals/{user_id}", response_model=schemas.UserGoals)
async def get_goals_by_user_id(
    user_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_trainer)
):
    """
    Obtener los objetivos del usuario por ID
    """
    # Verificar si el usuario existe
    user = db.query(models.User).filter(
        models.User.id == user_id
    ).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    return {
        "weight_goal": user.weight_goal,
        "body_fat_goal": user.body_fat_goal,
        "muscle_mass_goal": user.muscle_mass_goal,
        "activity_level_goal": user.activity_level_goal,
        "calories_goal": user.calories_goal,
        "protein_goal": user.protein_goal,
        "carbs_goal": user.carbs_goal,
        "fat_goal": user.fat_goal,
        "water_goal": user.water_goal,
        "steps_goal": user.steps_goal
    }
