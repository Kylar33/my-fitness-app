from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from model.model import Entrenador
from schemas.schemas import EntrenadorCreate
from database import SessionLocal

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

@router.post("/register/entrenador")
def register_entrenador(entrenador: EntrenadorCreate, db: Session = Depends(SessionLocal)):
    db_entrenador = db.query(Entrenador).filter(Entrenador.email == entrenador.email).first()
    if db_entrenador:
        raise HTTPException(status_code=400, detail="Email ya registrado")
    new_entrenador = Entrenador(
        nombre=entrenador.nombre,
        email=entrenador.email,
        especialidad=entrenador.especialidad
    )
    db.add(new_entrenador)
    db.commit()
    db.refresh(new_entrenador)
    return {"message": "Entrenador registrado exitosamente"}