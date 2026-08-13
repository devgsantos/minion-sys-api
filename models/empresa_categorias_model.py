from typing import Optional

from sqlalchemy import Column, func,  Integer, String, DateTime
from datetime import datetime

from sqlalchemy.orm import relationship

from models.base import Base
from .soft_delete import SoftDeleteQuery
from pydantic import BaseModel, constr


class EmpresaCategoriaModel(Base, SoftDeleteQuery):
    __tablename__ = 'empresa_categoria'

    empresa_categoria_id = Column('empresa_categoria_id', Integer, primary_key=True)
    titulo = Column('titulo', String(300), nullable=False)
    descricao = Column('descricao', String(500), nullable=True)
    sigla = Column('sigla', String(3), nullable=False)
    imagem = Column('imagem', String(300), nullable=True)
    data_cadastro = Column('data_cadastro', DateTime(timezone=False), default=func.now(), nullable=True)
    data_atualizacao = Column('data_atualizacao', DateTime(timezone=False), onupdate=func.now())
    data_exclusao = Column('data_exclusao', DateTime(timezone=False), nullable=True, default=None)

class EmpresaCategoriaBaseModel(BaseModel):
    empresa_categoria_id: int
    titulo: constr(max_length=300)
    descricao: Optional[constr(max_length=500)]
    sigla: constr(max_length=3)
    imagem: Optional[constr(max_length=300)]
    data_cadastro: Optional[datetime]
    data_atualizacao: Optional[datetime]
    data_exclusao: Optional[datetime]

    class Config:
        from_attributes = True