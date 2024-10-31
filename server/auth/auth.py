from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from model.model import Cliente_Create, Entrenador, Cliente, Entrenador_Create, List, Login, Rutina, RutinaCliente, RutinaClienteCreate, RutinaCreate  # Importa los modelos desde models.py
from database import SessionLocal
from pydantic import BaseModel, EmailStr

# Configuración para el cifrado de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configuración para JWT
SECRET_KEY = "YOUR_SECRET_KEY"  # Cambia esto por un valor seguro
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Creación del router
router = APIRouter()

# Dependencia para obtener la sesión de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Helpers para contraseña y token
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Registro de Entrenador
@router.post("/register/entrenador")
async def register_entrenador(entrenador: Entrenador_Create, db: Session = Depends(get_db)):
    # Verificar si el email ya existe
    if db.query(Entrenador).filter(Entrenador.email == entrenador.email).first():
        raise HTTPException(status_code=400, detail="Email ya registrado.")
    
    hashed_password = get_password_hash(entrenador.password)
    db_entrenador = Entrenador(nombre=entrenador.nombre, email=entrenador.email, hashed_password=hashed_password)
    db.add(db_entrenador)
    db.commit()
    db.refresh(db_entrenador)
    return {"message": "Entrenador registrado con éxito", "email": db_entrenador.email}

# Registro de Cliente
@router.post("/register/cliente")
async def register_cliente(cliente: Cliente_Create, db: Session = Depends(get_db)):
    # Verificar si el email ya existe
    if db.query(Cliente).filter(Cliente.email == cliente.email).first():
        raise HTTPException(status_code=400, detail="Email ya registrado.")
    
    hashed_password = get_password_hash(cliente.password)
    db_cliente = Cliente(nombre=cliente.nombre, email=cliente.email, hashed_password=hashed_password)
    db.add(db_cliente)
    db.commit()
    db.refresh(db_cliente)
    return {"message": "Cliente registrado con éxito", "email": db_cliente.email}

# Login
@router.post("/login")
async def login_user(login: Login, db: Session = Depends(get_db)):
    db_user = db.query(Entrenador).filter(Entrenador.email == login.email).first() or \
              db.query(Cliente).filter(Cliente.email == login.email).first()
    
    if not db_user or not verify_password(login.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": db_user.email}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

# Crear una nueva rutina
@router.post("/rutinas", response_model=Rutina)
async def create_rutina(rutina: RutinaCreate, db: Session = Depends(get_db)):
    db_rutina = Rutina(nombre=rutina.nombre, descripcion=rutina.descripcion)
    db.add(db_rutina)
    db.commit()
    db.refresh(db_rutina)
    return db_rutina

# Asignar rutina a un cliente
@router.post("/rutinas/asignar", response_model=RutinaClienteCreate)
async def assign_rutina(rutina_cliente: RutinaClienteCreate, db: Session = Depends(get_db)):
    # Verificar si la rutina existe
    rutina = db.query(Rutina).filter(Rutina.id == rutina_cliente.rutina_id).first()
    if not rutina:
        raise HTTPException(status_code=404, detail="Rutina no encontrada")

    # Verificar si el cliente existe
    cliente = db.query(Cliente).filter(Cliente.id == rutina_cliente.cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    db_rutina_cliente = RutinaCliente(
        cliente_id=rutina_cliente.cliente_id,
        rutina_id=rutina_cliente.rutina_id,
        fecha_inicio=rutina_cliente.fecha_inicio,
        fecha_fin=rutina_cliente.fecha_fin,
        progreso=rutina_cliente.progreso,
    )
    db.add(db_rutina_cliente)
    db.commit()
    db.refresh(db_rutina_cliente)
    return db_rutina_cliente



