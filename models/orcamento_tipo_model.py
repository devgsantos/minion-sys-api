from sqlalchemy import Column, func, Integer, ForeignKey, Boolean, DateTime, String
from sqlalchemy.orm import relationship
from datetime import datetime

from app.shared.helpers.validators import format_datetime
from models.base import Base
from .soft_delete import SoftDeleteQuery
from typing import Optional
from pydantic import BaseModel, field_validator


class OrcamentoTipoModel(Base, SoftDeleteQuery):
    __tablename__ = 'orcamento_tipo'

    orcamento_tipo_id = Column('orcamento_tipo_id', Integer, primary_key=True)
    titulo = Column('titulo', String(300), nullable=False)
    descricao = Column('descricao', String(500))
    data_cadastro = Column('data_cadastro', DateTime(timezone=False), nullable=False, server_default=func.now(),
                           default=func.now())
    data_atualizacao = Column('data_atualizacao', DateTime(timezone=False), onupdate=func.now())
    responsavel_cadastro_id = Column('responsavel_cadastro_id', Integer)
    empresa_id = Column('empresa_id', Integer, ForeignKey('empresa.empresa_id'), nullable=False)
    status = Column('status', Boolean, nullable=False, default=True)
    data_exclusao = Column('data_exclusao', DateTime)

    produto = relationship('ProdutoModel')

class OrcamentoTipoBaseModel(BaseModel):
    orcamento_tipo_id: Optional[int]
    quantidade_orcamento: int
    finalizado: bool
    data_cadastro: Optional[datetime]

    @field_validator('data_cadastro')
    def format_datetime(cls, value):
        return format_datetime(value)

    class Config:
        from_attributes = True