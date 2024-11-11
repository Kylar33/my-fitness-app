from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import users, routines, nutrition


app = FastAPI(title="Fitness Trainer API")

# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "API fitness ON"}


app.include_router(users.router, prefix="/api/v1", tags=["users"])
app.include_router(routines.router, prefix="/api/v1", tags=["routines"])
app.include_router(nutrition.router, prefix="/api/v1", tags=["nutrition"])