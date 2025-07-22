from typing import Optional

from pydantic import BaseModel, constr
from sqlalchemy import Column, func,  Integer, String
from sqlalchemy.orm import relationship

from models.base import Base

class PaisModel(Base):
    __tablename__ = 'pais'
    pais_id = Column('pais_id', Integer, primary_key=True)
    nome = Column('nome', String(300), nullable=False)
    codigo_area = Column('codigo_area', String(5), nullable=False)
    sigla = Column('sigla', String(2), nullable=False)
    bandeira = Column('bandeira', String(300))

class PaisBaseModel(BaseModel):
    pais_id: int
    nome: constr(max_length=300)
    codigo_area: constr(max_length=5)
    sigla: constr(max_length=2)
    bandeira: Optional[str]

    class Config:
        from_attributes = True
