# schemas.py

from pydantic import BaseModel, EmailStr, condecimal
from typing import List, Optional
from datetime import date

# Esquema para el Entrenador
class EntrenadorBase(BaseModel):
    nombre: str
    email: EmailStr
    especialidad: Optional[str] = None
    experiencia: Optional[int] = None
    telefono: Optional[str] = None

class EntrenadorCreate(EntrenadorBase):
    hashed_password: str

class Entrenador(EntrenadorBase):
    id: int
    clientes: List["Cliente"] = []
    rutinas: List["Rutina"] = []
    planes_nutricion: List["PlanNutricion"] = []

    class Config:
        orm_mode = True

# Esquema para el Cliente
class ClienteBase(BaseModel):
    nombre: str
    email: EmailStr
    objetivos: Optional[str] = None
    entrenador_id: Optional[int] = None

class ClienteCreate(ClienteBase):
    hashed_password: str

class Cliente(ClienteBase):
    id: int
    rutinas_cliente: List["RutinaCliente"] = []
    nutricion_cliente: List["NutricionCliente"] = []
    metricas: List["Metrica"] = []

    class Config:
        orm_mode = True

# Esquema para la Rutina
class RutinaBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    entrenador_id: int

class RutinaCreate(RutinaBase):
    pass

class Rutina(RutinaBase):
    id: int
    rutinas_cliente: List["RutinaCliente"] = []

    class Config:
        orm_mode = True

# Esquema para la RutinaCliente
class RutinaClienteBase(BaseModel):
    cliente_id: int
    rutina_id: int
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    progreso: Optional[str] = None

class RutinaClienteCreate(RutinaClienteBase):
    pass

class RutinaCliente(RutinaClienteBase):
    id: int

    class Config:
        orm_mode = True

# Esquema para el PlanNutricion
class PlanNutricionBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    entrenador_id: int

class PlanNutricionCreate(PlanNutricionBase):
    pass

class PlanNutricion(PlanNutricionBase):
    id: int
    nutricion_cliente: List["NutricionCliente"] = []

    class Config:
        orm_mode = True

# Esquema para la NutricionCliente
class NutricionClienteBase(BaseModel):
    cliente_id: int
    plan_nutricion_id: int
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    cumplimiento: Optional[str] = None

class NutricionClienteCreate(NutricionClienteBase):
    pass

class NutricionCliente(NutricionClienteBase):
    id: int

    class Config:
        orm_mode = True

# Esquema para la Metrica

Peso = condecimal(max_digits=5, decimal_places=2)
Grasa_corporal = condecimal(max_digits=5, decimal_places=2)
class MetricaBase(BaseModel):
    cliente_id: int
    fecha: date
    peso: Optional[Peso] = None
    grasa_corporal: Optional[Grasa_corporal] = None
    rendimiento: Optional[str] = None

class MetricaCreate(MetricaBase):
    pass

class Metrica(MetricaBase):
    id: int

    class Config:
        orm_mode = True
