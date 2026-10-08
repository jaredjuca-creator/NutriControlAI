from pydantic import BaseModel
from datetime import date


class PacienteCreate(BaseModel):

    nome: str
    idade: int
    telefone: str
    email: str
    peso: float
    altura: float
    objetivo: str
    sexo: str
    nivel_atividade: str


class PacienteUpdate(BaseModel):

    nome: str | None = None
    idade: int | None = None
    telefone: str | None = None
    email: str | None = None
    peso: float | None = None
    altura: float | None = None
    objetivo: str | None = None
    sexo: str | None = None
    nivel_atividade: str | None = None

class PacienteResponse(BaseModel):

    id: int
    nome: str
    idade: int
    telefone: str
    email: str
    peso: float
    altura: float
    objetivo: str
    sexo: str
    nivel_atividade: str

class Config:
    from_attributes = True


class AvaliacaoCreate(BaseModel):
    paciente_id: int
    peso: float
    altura: float
    data: date


class AvaliacaoResponse(BaseModel):
    id: int
    paciente_id: int
    peso: float
    altura: float
    data: date

class Config:
    from_attributes = True


class MetaCreate(BaseModel):
    paciente_id: int
    peso_meta: float
    objetivo: str
    data: date


class MetaResponse(BaseModel):
    id: int
    paciente_id: int
    peso_meta: float
    objetivo: str
    data: date

class Config:
    from_attributes = True