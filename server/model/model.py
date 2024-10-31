# Importaciones
from sqlalchemy import Column, Integer, String, Text, Date, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship
from database import Base
from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional, List

class Entrenador_Create(BaseModel):
    nombre: str
    email: EmailStr
    password: str

class Cliente_Create(BaseModel):
    nombre: str
    email: EmailStr
    password: str

class Login(BaseModel):
    email: EmailStr
    password: str

# Tabla de Entrenadores
class Entrenador(Base):
    __tablename__ = "entrenadores"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(200), nullable=False)
    especialidad = Column(String(100))
    experiencia = Column(Integer, comment="Años de experiencia")
    telefono = Column(String(15))
    
    clientes = relationship("Cliente", back_populates="entrenador")
    rutinas = relationship("Rutina", back_populates="entrenador")
    planes_nutricion = relationship("PlanNutricion", back_populates="entrenador")


# Tabla de Clientes
class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(200), nullable=False)
    objetivos = Column(Text, comment="Objetivos del cliente")
    entrenador_id = Column(Integer, ForeignKey("entrenadores.id", ondelete="SET NULL"))
    
    entrenador = relationship("Entrenador", back_populates="clientes")
    rutinas_cliente = relationship("RutinaCliente", back_populates="cliente")
    nutricion_cliente = relationship("NutricionCliente", back_populates="cliente")
    metricas = relationship("Metrica", back_populates="cliente")


# Tabla de Rutinas
class Rutina(Base):
    __tablename__ = "rutinas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text)
    entrenador_id = Column(Integer, ForeignKey("entrenadores.id", ondelete="CASCADE"))
    
    entrenador = relationship("Entrenador", back_populates="rutinas")
    rutinas_cliente = relationship("RutinaCliente", back_populates="rutina")


# Tabla de Rutina_Cliente
class RutinaCliente(Base):
    __tablename__ = "rutina_cliente"

    id = Column(Integer, primary_key=True, autoincrement=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id", ondelete="CASCADE"), nullable=False)
    rutina_id = Column(Integer, ForeignKey("rutinas.id", ondelete="CASCADE"), nullable=False)
    fecha_inicio = Column(Date)
    fecha_fin = Column(Date)
    progreso = Column(Text, comment="Progreso del cliente en la rutina")
    
    cliente = relationship("Cliente", back_populates="rutinas_cliente")
    rutina = relationship("Rutina", back_populates="rutinas_cliente")


# Tabla de Planes de Nutrición
class PlanNutricion(Base):
    __tablename__ = "planes_nutricion"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text)
    entrenador_id = Column(Integer, ForeignKey("entrenadores.id", ondelete="CASCADE"))
    
    entrenador = relationship("Entrenador", back_populates="planes_nutricion")
    nutricion_cliente = relationship("NutricionCliente", back_populates="plan_nutricion")


# Tabla de Nutricion_Cliente
class NutricionCliente(Base):
    __tablename__ = "nutricion_cliente"

    id = Column(Integer, primary_key=True, autoincrement=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id", ondelete="CASCADE"), nullable=False)
    plan_nutricion_id = Column(Integer, ForeignKey("planes_nutricion.id", ondelete="CASCADE"), nullable=False)
    fecha_inicio = Column(Date)
    fecha_fin = Column(Date)
    cumplimiento = Column(Text, comment="Cumplimiento del cliente con el plan de nutrición")
    
    cliente = relationship("Cliente", back_populates="nutricion_cliente")
    plan_nutricion = relationship("PlanNutricion", back_populates="nutricion_cliente")


# Tabla de Métricas de Progreso
class Metrica(Base):
    __tablename__ = "metricas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id", ondelete="CASCADE"), nullable=False)
    fecha = Column(Date, nullable=False)
    peso = Column(DECIMAL(5, 2))
    grasa_corporal = Column(DECIMAL(5, 2))
    rendimiento = Column(String(100))
    
    cliente = relationship("Cliente", back_populates="metricas")


# Rutinas
class RutinaBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None

class RutinaCreate(RutinaBase):
    pass

class Rutina(RutinaBase):
    id: int
    entrenador_id: int

    class Config:
        orm_mode = True

class RutinaClienteCreate(BaseModel):
    cliente_id: int
    rutina_id: int
    fecha_inicio: date
    fecha_fin: Optional[date] = None
    progreso: Optional[str] = None