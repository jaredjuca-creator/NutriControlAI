from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date
from database import Base


class Paciente(Base):
    __tablename__ = "pacientes"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    idade = Column(Integer)
    sexo = Column(String)
    telefone = Column(String)
    email = Column(String)
    peso = Column(Float)
    altura = Column(Float)
    objetivo = Column(String)
    nivel_atividade = Column(String)


class Avaliacao(Base):
    __tablename__ = "avaliacoes"

    id = Column(Integer, primary_key=True, index=True)
    paciente_id = Column(Integer, ForeignKey("pacientes.id"), nullable=False)
    peso = Column(Float)
    altura = Column(Float)
    data = Column(Date)


class Meta(Base):
    __tablename__ = "metas"

    id = Column(Integer, primary_key=True, index=True)
    paciente_id = Column(Integer, ForeignKey("pacientes.id"), nullable=False)
    peso_meta = Column(Float, nullable=False)
    objetivo = Column(String, nullable=False)
    data = Column(Date)