from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Any
from config.database import get_db
from schemas.schemas import UserGoals
from models.models import User
from utils.auth import get_current_user

router = APIRouter(
    prefix="/goals",
    tags=["goals"]
)

@router.get("/user/goals/", response_model=UserGoals)
async def get_user_goals(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Obtener los objetivos del usuario actual
    """
    # Obtener el usuario completo de la base de datos usando el token
    user = db.query(User).filter(User.email == current_user.get("email")).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )

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

@router.put("/user/goals/", response_model=UserGoals)
async def update_user_goals(
    goals: UserGoals,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Actualizar los objetivos del usuario actual
    """
    user = db.query(User).filter(User.email == current_user.get("email")).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Actualizar los objetivos
    for field, value in goals.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    
    try:
        db.commit()
        db.refresh(user)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se pudieron actualizar los objetivos"
        )
    
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

@router.post("/user/goals/calculate", response_model=UserGoals)
async def calculate_recommended_goals(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Calcular objetivos recomendados para el usuario
    """
    user = db.query(User).filter(User.email == current_user.get("email")).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )

    # Obtener las últimas métricas del usuario
    latest_metrics = db.query(User).filter(
        User.email == user.email
    ).order_by(User.created_at.desc()).first()

    # Cálculos básicos para objetivos recomendados
    weight = latest_metrics.weight if latest_metrics else 70  # peso por defecto
    height = user.height or 170  # altura en cm

    # Cálculo del BMR usando la fórmula de Harris-Benedict
    if latest_metrics and latest_metrics.weight:
        bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * 25)  # 25 es la edad por defecto
        
        # Establecer objetivos recomendados
        recommended_goals = {
            "weight_goal": round(weight * 0.9, 1) if user.fitness_goal == "pérdida de peso" else weight,
            "body_fat_goal": 15 if user.fitness_goal == "pérdida de peso" else 20,
            "muscle_mass_goal": round(weight * 0.75, 1),
            "activity_level_goal": 4,  # 4 días de ejercicio por semana
            "calories_goal": int(bmr * 1.2),  # Factor de actividad sedentaria
            "protein_goal": int(weight * 2),  # 2g por kg de peso
            "carbs_goal": int((bmr * 1.2 * 0.5) / 4),  # 50% de calorías de carbos
            "fat_goal": int((bmr * 1.2 * 0.3) / 9),  # 30% de calorías de grasas
            "water_goal": round(weight * 0.033, 1),  # 33ml por kg de peso
            "steps_goal": 10000  # Objetivo estándar de pasos
        }

        # Actualizar los objetivos del usuario
        for field, value in recommended_goals.items():
            setattr(user, field, value)

        try:
            db.commit()
            db.refresh(user)
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se pudieron actualizar los objetivos recomendados"
            )

        return recommended_goals
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No hay suficientes datos para calcular objetivos recomendados"
        )