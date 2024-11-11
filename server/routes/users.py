from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from config.database import get_db
from models.user import User
from schemas.user import UserCreate, User as UserSchema
from middleware.auth import get_current_trainer
from utils.auth import get_password_hash

router = APIRouter()

@router.post("/users/", response_model=UserSchema)
async def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_trainer = Depends(get_current_trainer)
):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        password=hashed_password,
        first_name=user.first_name,
        last_name=user.last_name,
        trainer_id=current_trainer.id
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/users/", response_model=List[UserSchema])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_trainer = Depends(get_current_trainer)
):
    users = db.query(User).filter(
        User.trainer_id == current_trainer.id
    ).offset(skip).limit(limit).all()
    return users

@router.get("/users/{user_id}", response_model=UserSchema)
async def read_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_trainer = Depends(get_current_trainer)
):
    user = db.query(User).filter(
        User.id == user_id,
        User.trainer_id == current_trainer.id
    ).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user