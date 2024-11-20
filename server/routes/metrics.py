from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import List
from datetime import date, datetime, timedelta
from config.database import get_db
import models.models as models
import schemas.schemas as schemas
from utils.auth import get_current_user, get_current_trainer
from utils.metrics import calculate_bmi, calculate_progress_stats, get_user_completion_rates
from utils.reports import generate_user_report

router = APIRouter(prefix="/metrics", tags=["metrics"])

@router.post("/user/{user_id}/metrics", response_model=schemas.UserMetrics)
async def create_user_metrics(
    user_id: int,
    metrics: schemas.UserMetricsCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verificar permisos
    if current_user["role"] not in ["admin", "trainer"] and current_user["user"].id != user_id:
        raise HTTPException(status_code=403, detail="No tienes permiso para crear métricas para este usuario")
    
    # Verificar si el usuario existe
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Crear métricas
    db_metrics = models.UserMetrics(
        user_id=user_id,
        date=date.today(),
        **metrics.dict()
    )
    
    # Calcular BMI si se proporcionan peso y altura
    if metrics.weight and user.height:
        db_metrics.bmi = calculate_bmi(metrics.weight, user.height)
    
    db.add(db_metrics)
    db.commit()
    db.refresh(db_metrics)
    return db_metrics

@router.get("/user/{user_id}/metrics", response_model=List[schemas.UserMetrics])
async def get_user_metrics(
    user_id: int,
    start_date: date = None,
    end_date: date = None,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verificar permisos
    if current_user["role"] not in ["admin", "trainer"] and current_user["user"].id != user_id:
        raise HTTPException(status_code=403, detail="No tienes permiso para ver las métricas de este usuario")
    
    query = db.query(models.UserMetrics).filter(models.UserMetrics.user_id == user_id)
    
    if start_date:
        query = query.filter(models.UserMetrics.date >= start_date)
    if end_date:
        query = query.filter(models.UserMetrics.date <= end_date)
    
    return query.order_by(models.UserMetrics.date.desc()).all()

@router.get("/user/{user_id}/progress", response_model=schemas.UserStats)
async def get_user_progress(
    user_id: int,
    start_date: date = None,
    end_date: date = None,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verificar permisos
    if current_user["role"] not in ["admin", "trainer"] and current_user["user"].id != user_id:
        raise HTTPException(status_code=403, detail="No tienes permiso para ver el progreso de este usuario")
    
    if not start_date:
        start_date = date.today() - timedelta(days=30)
    if not end_date:
        end_date = date.today()
    
    # Obtener estadísticas de progreso
    completion_rates = get_user_completion_rates(db, user_id, start_date, end_date)
    
    # Obtener métricas
    metrics = db.query(models.UserMetrics).filter(
        models.UserMetrics.user_id == user_id,
        models.UserMetrics.date.between(start_date, end_date)
    ).order_by(models.UserMetrics.date).all()
    
    metrics_stats = calculate_progress_stats(metrics)
    
    return {
        "total_workouts": completion_rates["workout"]["total"],
        "completed_workouts": completion_rates["workout"]["completed"],
        "completion_rate": completion_rates["workout"]["rate"],
        "initial_weight": metrics_stats["initial_weight"] if metrics_stats else None,
        "current_weight": metrics_stats["current_weight"] if metrics_stats else None,
        "weight_change": metrics_stats["weight_change"] if metrics_stats else None,
        "initial_body_fat": metrics_stats["initial_body_fat"] if metrics_stats else None,
        "current_body_fat": metrics_stats["current_body_fat"] if metrics_stats else None,
        "body_fat_change": metrics_stats["body_fat_change"] if metrics_stats else None,
    }

@router.get("/user/{user_id}/report")

async def get_user_report(
    user_id: int,
    start_date: date = None,
    end_date: date = None,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user["role"] not in ["admin", "trainer"] and current_user["user"].id != user_id:
        raise HTTPException(status_code=403, detail="No tienes permiso para generar reportes para este usuario")
    
    if not start_date:
        start_date = date.today() - timedelta(days=30)
    if not end_date:
        end_date = date.today()
    
    
    try:
        pdf_content = generate_user_report(db, user_id, start_date, end_date)
        return Response(
            content=pdf_content,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=report_{user_id}_{start_date}_{end_date}.pdf"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando el reporte: {str(e)}")