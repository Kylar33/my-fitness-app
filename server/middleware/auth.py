from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from config.database import get_db
from models.user import User, Trainer
import os

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, 
            os.getenv("SECRET_KEY"), 
            algorithms=[os.getenv("ALGORITHM")]
        )
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.email == email).first()
    trainer = db.query(Trainer).filter(Trainer.email == email).first()
    
    if user is None and trainer is None:
        raise credentials_exception
    
    return user if user else trainer

async def get_current_trainer(
    current_user = Depends(get_current_user)
):
    if not isinstance(current_user, Trainer):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough privileges"
        )
    return current_user
