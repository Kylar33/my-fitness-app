from fastapi import FastAPI
from database import SessionLocal, engine
from sqlalchemy import text
from model.model import Base
from auth.auth import router as auth_router

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/test_db")
async def test_db():
    db = SessionLocal()
    try: 
        db.execute(text("SELECT 1"))
        return {"message": "Database connection successful"}
    except Exception as e:
        return {"message": "Database connection failed", "error": str(e)}
    finally:
        db.close()

Base.metadata.create_all(bind=engine)

app.include_router(auth_router, prefix="/auth")