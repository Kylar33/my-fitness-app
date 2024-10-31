from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from model.model import Cliente, Rutina, RutinaCliente, RutinaClienteCreate, RutinaCreate  # Asegúrate de importar tus modelos
from database import SessionLocal
from typing import List
from datetime import date

router = APIRouter()

# Dependencia para obtener la sesión de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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

# Obtener todas las rutinas
@router.get("/rutinas", response_model=List[Rutina])
async def get_rutinas(db: Session = Depends(get_db)):
    return db.query(Rutina).all()

# Obtener rutinas de un cliente específico
@router.get("/clientes/{cliente_id}/rutinas", response_model=List[Rutina])
async def get_rutinas_cliente(cliente_id: int, db: Session = Depends(get_db)):
    rutinas_cliente = db.query(RutinaCliente).filter(RutinaCliente.cliente_id == cliente_id).all()
    return [db.query(Rutina).filter(Rutina.id == rc.rutina_id).first() for rc in rutinas_cliente]
