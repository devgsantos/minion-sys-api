from datetime import datetime

from pydantic import BaseModel, field_validator
from sqlalchemy import Column, func,  Integer, DateTime, String
from sqlalchemy.orm import relationship

from models.base import Base
from models.soft_delete import SoftDeleteQuery
from typing import Optional
from app.shared.helpers.validators import format_datetime



class EstoqueTipoModel(Base, SoftDeleteQuery):
    __tablename__ = 'estoque_tipo'
    estoque_tipo_id = Column('estoque_tipo_id', Integer, primary_key=True)
    titulo = Column('titulo', String(500), nullable=False)
    descricao = Column('descricao', String(1000), nullable=True)
    data_cadastro = Column('data_cadastro', DateTime(timezone=False), default=func.now(), nullable=False)
    data_atualizacao = Column('data_atualizacao', DateTime(timezone=False), onupdate=func.now())
    data_exclusao = Column('data_exclusao', DateTime(timezone=False), nullable=True, default=None)


class EstoqueTipoBaseModel(BaseModel):
    estoque_tipo_id: int
    titulo: str
    descricao: str

    class Config:
        from_attributes = True
