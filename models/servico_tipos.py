from pydantic import BaseModel, constr, field_validator
from sqlalchemy import Column, func,  Integer, String, Numeric, ForeignKey, DateTime, Boolean
from models.base import Base
from datetime import datetime
from typing import List, Optional
from app.shared.helpers.validators import format_datetime
from .soft_delete import SoftDeleteQuery


class ServicoTipoModel(Base, SoftDeleteQuery):
    __tablename__ = 'servico_tipo'
    servico_tipo_id = Column('servico_tipo_id', Integer, primary_key=True)
    titulo = Column('titulo', String(300), nullable=False)
    descricao = Column('descricao', String(500))
    data_cadastro = Column('data_cadastro', DateTime(timezone=False), nullable=False, server_default=func.now(), default=func.now())
    data_atualizacao = Column('data_atualizacao', DateTime(timezone=False), onupdate=func.now())
    responsavel_cadastro_id = Column('responsavel_cadastro_id', Integer)
    empresa_id = Column('empresa_id', Integer, ForeignKey('empresa.empresa_id'), nullable=False)
    data_exclusao = Column('data_exclusao', DateTime)

class ServicoTipoBaseModel(BaseModel):
    servico_tipo_id: int
    titulo: constr(max_length=300)
    descricao: Optional[constr(max_length=500)]
    imagem: Optional[str]
    data_cadastro: datetime
    data_atualizacao: Optional[datetime]
    responsavel_cadastro_id: int
    data_exclusao: Optional[datetime]

    @field_validator('data_cadastro', 'data_atualizacao', 'data_exclusao')
    def format_datetime(cls, value):
        return format_datetime(value)

    class Config:
        from_attributes = True

class ServicoTipoRequestModel(BaseModel):
    titulo: constr(max_length=300)
    descricao: Optional[constr(max_length=500)]
    empresa_id: int