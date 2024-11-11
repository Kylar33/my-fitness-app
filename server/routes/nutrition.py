from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from config.database import get_db
from models.nutrition import NutritionPlan, Meal
from schemas.nutrition import NutritionPlanCreate, NutritionPlan as NutritionPlanSchema
from middleware.auth import get_current_trainer

router = APIRouter()

@router.post("/nutrition-plans/", response_model=NutritionPlanSchema)
async def create_nutrition_plan(
    plan: NutritionPlanCreate,
    db: Session = Depends(get_db),
    current_trainer = Depends(get_current_trainer)
):
    db_plan = NutritionPlan(
        name=plan.name,
        description=plan.description,
        trainer_id=current_trainer.id
    )
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)

    for meal in plan.meals:
        db_meal = Meal(
            **meal.dict(),
            nutrition_plan_id=db_plan.id
        )
        db.add(db_meal)
    
    db.commit()
    db.refresh(db_plan)
    return db_plan

@router.get("/nutrition-plans/", response_model=List[NutritionPlanSchema])
async def read_nutrition_plans(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_trainer = Depends(get_current_trainer)
):
    plans = db.query(NutritionPlan).filter(
        NutritionPlan.trainer_id == current_trainer.id
    ).offset(skip).limit(limit).all()
    return plans

@router.get("/nutrition-plans/{plan_id}", response_model=NutritionPlanSchema)
async def read_nutrition_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current_trainer = Depends(get_current_trainer)
):
    plan = db.query(NutritionPlan).filter(
        NutritionPlan.id == plan_id,
        NutritionPlan.trainer_id == current_trainer.id
    ).first()
    if plan is None:
        raise HTTPException(status_code=404, detail="Nutrition plan not found")
    return plan