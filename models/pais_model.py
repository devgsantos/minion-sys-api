from pydantic import BaseModel
from sqlalchemy import Column, Integer, String
from .base import Base

class PaisModel(Base):
    __tablename__ = 'pais'
    pais_id = Column('pais_id', Integer, primary_key=True)
    nome = Column('nome', String(300), nullable=False)
    codigo_area = Column('codigo_area', String(5), nullable=False)
    sigla = Column('sigla', String(2), nullable=False)
    bandeira = Column('bandeira', String(300))

class PaisesSchema(BaseModel):
    PaisId: int
    Nome: str
    CodigoArea: str
    Sigla: str
    Bandeira: str = None
