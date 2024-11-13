from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class TrainerBase(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class TrainerCreate(TrainerBase):
    password: str

class Trainer(TrainerBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

class UserBase(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class UserCreate(UserBase):
    email: str
    password: str
    first_name: str
    last_name: str
    trainer_id: int

class User(UserBase):
    id: int
    trainer_id: int
    created_at: datetime

    class Config:
        orm_mode = True