from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import date
from config.database import get_db
from models.assignments import UserRoutine, UserNutritionPlan
from models.user import User
from models.routine import Routine
from models.nutrition import NutritionPlan
from schemas.assignments import (
    RoutineAssignment,
    NutritionPlanAssignment,
    AssignmentResponse
)
from middleware.auth import get_current_trainer

router = APIRouter()

@router.post("/assign/routine", response_model=AssignmentResponse)
async def assign_routine(
    assignment: RoutineAssignment,
    db: Session = Depends(get_db),
    current_trainer = Depends(get_current_trainer)
):
    # Verificar que el usuario pertenece al entrenador
    user = db.query(User).filter(
        User.id == assignment.user_id,
        User.trainer_id == current_trainer.id
    ).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Verificar que la rutina pertenece al entrenador
    routine = db.query(Routine).filter(
        Routine.id == assignment.routine_id,
        Routine.trainer_id == current_trainer.id
    ).first()
    if not routine:
        raise HTTPException(status_code=404, detail="Routine not found")

    # Crear la asignación
    db_assignment = UserRoutine(**assignment.dict())
    db.add(db_assignment)
    db.commit()
    db.refresh(db_assignment)
    return db_assignment

@router.post("/assign/nutrition", response_model=AssignmentResponse)
async def assign_nutrition_plan(
    assignment: NutritionPlanAssignment,
    db: Session = Depends(get_db),
    current_trainer = Depends(get_current_trainer)
):
    # Verificaciones similares para plan nutricional
    user = db.query(User).filter(
        User.id == assignment.user_id,
        User.trainer_id == current_trainer.id
    ).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    plan = db.query(NutritionPlan).filter(
        NutritionPlan.id == assignment.nutrition_plan_id,
        NutritionPlan.trainer_id == current_trainer.id
    ).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Nutrition plan not found")

    db_assignment = UserNutritionPlan(**assignment.dict())
    db.add(db_assignment)
    db.commit()
    db.refresh(db_assignment)
    return db_assignment

@router.get("/user/{user_id}/assignments")
async def get_user_assignments(
    user_id: int,
    db: Session = Depends(get_db),
    current_trainer = Depends(get_current_trainer)
):
    user = db.query(User).filter(
        User.id == user_id,
        User.trainer_id == current_trainer.id
    ).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    routine_assignments = db.query(UserRoutine).filter(
        UserRoutine.user_id == user_id,
        UserRoutine.end_date >= date.today()
    ).all()

    nutrition_assignments = db.query(UserNutritionPlan).filter(
        UserNutritionPlan.user_id == user_id,
        UserNutritionPlan.end_date >= date.today()
    ).all()

    return {
        "routines": routine_assignments,
        "nutrition_plans": nutrition_assignments
    }