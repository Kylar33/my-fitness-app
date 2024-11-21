from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta
import secrets
from config.database import get_db
import models.models as models
import schemas.schemas as schemas
from utils.auth import get_current_admin, get_current_trainer, get_password_hash
from utils.email import send_reset_email

router = APIRouter(prefix="/admin", tags=["admin"])

class TrainerUpdate(BaseModel):
    email: str
    full_name: str
    password: Optional[str] = None
    specialization: Optional[str] = None
    experience_years: Optional[int] = None
    certification: Optional[str] = None
    biography: Optional[str] = None
    
    class Config:
        from_attributes = True

@router.post("/trainers/", response_model=schemas.Trainer)
def create_trainer(
    trainer: schemas.TrainerCreate,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    # Verificar si el email ya existe
    existing_trainer = db.query(models.Trainer).filter(models.Trainer.email == trainer.email).first()
    if existing_trainer:
        raise HTTPException(
            status_code=400,
            detail="Email ya registrado"
        )

    db_trainer = models.Trainer(
        email=trainer.email,
        hashed_password=get_password_hash(trainer.password),
        full_name=trainer.full_name,
        specialization=trainer.specialization,
        experience_years=trainer.experience_years,
        certification=trainer.certification,
        biography=trainer.biography,
        admin_id=current_user["user"].id
    )
    db.add(db_trainer)
    db.commit()
    db.refresh(db_trainer)
    return db_trainer

@router.get("/trainers/", response_model=List[schemas.Trainer])
def read_trainers(
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    trainers = db.query(models.Trainer).offset(skip).limit(limit).all()
    return trainers

@router.post("/users/", response_model=schemas.User)
def create_user(
    user: schemas.UserCreate,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    # Verificar si el email ya existe
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="El email ya está registrado"
        )
    
    # Verificar que el trainer existe si se proporciona
    if user.trainer_id:
        trainer = db.query(models.Trainer).filter(models.Trainer.id == user.trainer_id).first()
        if not trainer:
            raise HTTPException(
                status_code=404,
                detail="Entrenador no encontrado"
            )
    
    # Crear nuevo usuario
    db_user = models.User(
        email=user.email,
        hashed_password=get_password_hash(user.password),
        full_name=user.full_name,
        trainer_id=user.trainer_id,
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
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users

@router.put("/users/{user_id}", response_model=schemas.User)
async def update_user(
    user_id: int,
    user_data: schemas.UserUpdate,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    try:
        db_user = db.query(models.User).filter(models.User.id == user_id).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        existing_user = db.query(models.User).filter(
            models.User.email == user_data.email,
            models.User.id != user_id
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="El email ya está en uso"
            )
        
        for key, value in user_data.dict(exclude_unset=True).items():
            if key == "password" and value:
                setattr(db_user, "hashed_password", get_password_hash(value))
            else:
                setattr(db_user, key, value)
        
        db.commit()
        db.refresh(db_user)
        return db_user
        
    except HTTPException as e:
        raise e
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(db_user)
    db.commit()
    return {"message": "User deleted"}

@router.get("/workout-plans/", response_model=List[schemas.WorkoutPlan])
async def read_workout_plans(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin)
):
    plans = db.query(models.WorkoutPlan)\
        .options(joinedload(models.WorkoutPlan.exercises))\
        .offset(skip)\
        .limit(limit)\
        .all()
    return plans

@router.get("/routines/", response_model=List[schemas.Routine])
def read_routines(
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    routines = db.query(models.Routine).offset(skip).limit(limit).all()
    return routines

@router.post("/routines/", response_model=schemas.Routine)
def create_routine(
    routine: schemas.RoutineCreate,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    try:
        db_routine = models.Routine(
            name=routine.name,
            description=routine.description
        )
        db.add(db_routine)
        db.flush()

        for exercise in routine.exercises:
            db_exercise = models.Exercise(
                **exercise.dict(),
                routine_id=db_routine.id
            )
            db.add(db_exercise)

        db.commit()
        db.refresh(db_routine)
        return db_routine
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put("/routines/{routine_id}", response_model=schemas.Routine)
def update_routine(
    routine_id: int,
    routine_data: schemas.RoutineUpdate,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    db_routine = db.query(models.Routine).filter(models.Routine.id == routine_id).first()
    if not db_routine:
        raise HTTPException(status_code=404, detail="Routine not found")
    
    for field, value in routine_data.dict(exclude_unset=True).items():
        if field != "exercises":
            setattr(db_routine, field, value)
    
    if routine_data.exercises is not None:
        # Delete existing exercises
        db.query(models.Exercise).filter(models.Exercise.routine_id == routine_id).delete()
        
        # Add new exercises
        for exercise in routine_data.exercises:
            db_exercise = models.Exercise(
                **exercise.dict(),
                routine_id=routine_id
            )
            db.add(db_exercise)
    
    try:
        db.commit()
        db.refresh(db_routine)
        return db_routine
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/routines/{routine_id}")
def delete_routine(
    routine_id: int,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    db_routine = db.query(models.Routine).filter(models.Routine.id == routine_id).first()
    if not db_routine:
        raise HTTPException(status_code=404, detail="Routine not found")
    
    db.delete(db_routine)
    db.commit()
    return {"message": "Routine deleted"}

@router.get("/nutrition-plans/", response_model=List[schemas.NutritionPlan])
def read_nutrition_plans(
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    nutrition_plans = db.query(models.NutritionPlan)\
        .options(joinedload(models.NutritionPlan.meals))\
        .offset(skip)\
        .limit(limit)\
        .all()
    return nutrition_plans

@router.put("/trainers/{trainer_id}", response_model=schemas.Trainer)
async def update_trainer(
    trainer_id: int,
    trainer_data: TrainerUpdate,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    db_trainer = db.query(models.Trainer).filter(models.Trainer.id == trainer_id).first()
    if not db_trainer:
        raise HTTPException(status_code=404, detail="Trainer not found")
    
    existing_trainer = db.query(models.Trainer).filter(
        models.Trainer.email == trainer_data.email,
        models.Trainer.id != trainer_id
    ).first()
    if existing_trainer:
        raise HTTPException(
            status_code=400,
            detail="Email ya está en uso"
        )
    
    for key, value in trainer_data.dict(exclude_unset=True).items():
        if key == "password" and value:
            setattr(db_trainer, "hashed_password", get_password_hash(value))
        else:
            setattr(db_trainer, key, value)
    
    try:
        db.commit()
        db.refresh(db_trainer)
        return db_trainer
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/trainers/{trainer_id}")
def delete_trainer(
    trainer_id: int,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    db_trainer = db.query(models.Trainer).filter(models.Trainer.id == trainer_id).first()
    if not db_trainer:
        raise HTTPException(status_code=404, detail="Trainer not found")
    
    db.delete(db_trainer)
    db.commit()
    return {"message": "Trainer deleted"}

# Continúa desde el código anterior...

reset_tokens = {}

@router.post("/create-admin/", response_model=schemas.Admin)
async def create_admin(
    admin: schemas.AdminCreate,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    # Verificar si el email ya existe
    existing_admin = db.query(models.Admin).filter(models.Admin.email == admin.email).first()
    if existing_admin:
        raise HTTPException(
            status_code=400,
            detail="Email ya registrado"
        )

    db_admin = models.Admin(
        email=admin.email,
        hashed_password=get_password_hash(admin.password),
        full_name=admin.full_name
    )
    db.add(db_admin)
    db.commit()
    db.refresh(db_admin)
    return db_admin

@router.get("/admins/", response_model=List[schemas.Admin])
async def get_admins(
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    admins = db.query(models.Admin).offset(skip).limit(limit).all()
    return admins

@router.put("/admin/{admin_id}", response_model=schemas.Admin)
async def update_admin(
    admin_id: int,
    admin_data: schemas.AdminUpdate,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    db_admin = db.query(models.Admin).filter(models.Admin.id == admin_id).first()
    if not db_admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    
    # Verificar email único
    if admin_data.email != db_admin.email:
        existing_admin = db.query(models.Admin).filter(
            models.Admin.email == admin_data.email,
            models.Admin.id != admin_id
        ).first()
        if existing_admin:
            raise HTTPException(
                status_code=400,
                detail="Email ya está en uso"
            )
    
    for key, value in admin_data.dict(exclude_unset=True).items():
        if key == "password" and value:
            setattr(db_admin, "hashed_password", get_password_hash(value))
        else:
            setattr(db_admin, key, value)
    
    try:
        db.commit()
        db.refresh(db_admin)
        return db_admin
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/admin/{admin_id}")
async def delete_admin(
    admin_id: int,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    # Verificar que no se está eliminando a sí mismo
    if current_user["user"].id == admin_id:
        raise HTTPException(
            status_code=400,
            detail="No puedes eliminarte a ti mismo"
        )

    db_admin = db.query(models.Admin).filter(models.Admin.id == admin_id).first()
    if not db_admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    
    db.delete(db_admin)
    db.commit()
    return {"message": "Admin deleted"}

@router.post("/request-password-reset/")
async def request_password_reset(
    request: schemas.AdminLoginReset,
    db: Session = Depends(get_db)
):
    # Buscar en todas las tablas
    user = None
    admin = db.query(models.Admin).filter(models.Admin.email == request.email).first()
    trainer = db.query(models.Trainer).filter(models.Trainer.email == request.email).first()
    user = db.query(models.User).filter(models.User.email == request.email).first()

    if not any([admin, trainer, user]):
        # Por seguridad, no revelamos si el email existe o no
        return {"message": "Si el email existe, recibirás instrucciones para resetear tu contraseña"}

    # Generar token único
    token = secrets.token_urlsafe(32)
    reset_tokens[token] = {
        "email": request.email,
        "expires": datetime.utcnow() + timedelta(hours=1)
    }

    # Enviar email
    try:
        send_reset_email(request.email, token)
        return {"message": "Si el email existe, recibirás instrucciones para resetear tu contraseña"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Error al enviar el email de recuperación"
        )

@router.post("/reset-password/")
async def reset_password(
    reset_data: schemas.PasswordReset,
    db: Session = Depends(get_db)
):
    token_data = reset_tokens.get(reset_data.token)
    if not token_data:
        raise HTTPException(status_code=400, detail="Token inválido")
    
    if datetime.utcnow() > token_data["expires"]:
        del reset_tokens[reset_data.token]
        raise HTTPException(status_code=400, detail="Token expirado")

    # Actualizar contraseña en la tabla correspondiente
    user = None
    admin = db.query(models.Admin).filter(models.Admin.email == token_data["email"]).first()
    trainer = db.query(models.Trainer).filter(models.Trainer.email == token_data["email"]).first()
    user = db.query(models.User).filter(models.User.email == token_data["email"]).first()

    new_password_hash = get_password_hash(reset_data.new_password)

    try:
        if admin:
            admin.hashed_password = new_password_hash
        elif trainer:
            trainer.hashed_password = new_password_hash
        elif user:
            user.hashed_password = new_password_hash
        else:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        db.commit()
        del reset_tokens[reset_data.token]
        return {"message": "Contraseña actualizada exitosamente"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Error al actualizar la contraseña"
        )

@router.get("/dashboard/stats")
async def get_dashboard_stats(
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    total_users = db.query(models.User).count()
    total_trainers = db.query(models.Trainer).count()
    total_workout_plans = db.query(models.WorkoutPlan).count()
    total_nutrition_plans = db.query(models.NutritionPlan).count()
    
    # Estadísticas de los últimos 30 días
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    new_users = db.query(models.User).filter(
        models.User.created_at >= thirty_days_ago
    ).count() if hasattr(models.User, 'created_at') else 0
    
    new_trainers = db.query(models.Trainer).filter(
        models.Trainer.created_at >= thirty_days_ago
    ).count() if hasattr(models.Trainer, 'created_at') else 0

    return {
        "total_stats": {
            "users": total_users,
            "trainers": total_trainers,
            "workout_plans": total_workout_plans,
            "nutrition_plans": total_nutrition_plans
        },
        "monthly_stats": {
            "new_users": new_users,
            "new_trainers": new_trainers
        }
    }

# routes/admin.py

@router.get("/users/{user_id}/plans")
async def get_user_plans(
    user_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin)
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Cargar explícitamente las relaciones
    workout_plans = [
        {
            "id": plan.id,
            "name": plan.name,
            "description": plan.description,
            "exercises": [
                {
                    "id": exercise.id,
                    "name": exercise.name,
                    "sets": exercise.sets,
                    "reps": exercise.reps
                }
                for exercise in plan.exercises
            ]
        }
        for plan in user.workout_plans
    ]
    
    nutrition_plans = [
        {
            "id": plan.id,
            "name": plan.name,
            "description": plan.description,
            "meals": [
                {
                    "id": meal.id,
                    "name": meal.name,
                    "description": meal.description,
                    "calories": meal.calories
                }
                for meal in plan.meals
            ]
        }
        for plan in user.nutrition_plans
    ]
    
    return {
        "workout_plans": workout_plans,
        "nutrition_plans": nutrition_plans
    }

@router.get("/system/health")
async def check_system_health(
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    try:
        # Verificar conexión a la base de datos
        db.execute("SELECT 1")
        
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Sistema no disponible: {str(e)}"
        )