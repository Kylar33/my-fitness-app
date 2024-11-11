import os
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from config.database import get_db
from models.user import User, Trainer
from schemas.user import UserCreate, TrainerCreate
from utils.auth import (
    verify_password,
    get_password_hash,
    create_access_token
)

router = APIRouter()

@router.post("/register/trainer")
def register_trainer(trainer: TrainerCreate, db: Session = Depends(get_db)):
    db_trainer = db.query(Trainer).filter(Trainer.email == trainer.email).first()
    if db_trainer:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(trainer.password)
    db_trainer = Trainer(
        email=trainer.email,
        password=hashed_password,
        first_name=trainer.first_name,
        last_name=trainer.last_name
    )
    db.add(db_trainer)
    db.commit()
    db.refresh(db_trainer)
    return db_trainer

@router.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == form_data.username).first()
    trainer = db.query(Trainer).filter(Trainer.email == form_data.username).first()
    
    if not user and not trainer:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    auth_user = user if user else trainer
    if not verify_password(form_data.password, auth_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(
        minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
    )
    access_token = create_access_token(
        data={"sub": auth_user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}