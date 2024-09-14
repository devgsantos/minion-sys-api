from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, condecimal, constr, field_validator
from sqlalchemy import Column, func,  Integer, String, Numeric, ForeignKey, DateTime, Boolean, Float
from models.base import Base
from .produto_model import ProdutoBaseModel
from .soft_delete import SoftDeleteQuery
from app.shared.helpers.validators import format_datetime


class ServicoModel(Base, SoftDeleteQuery):
    __tablename__ = 'servico'
    produto_id = Column('servico_id', Integer, primary_key=True)
    titulo = Column('titulo', String(500), nullable=False)
    preco_mao_de_obra = Column('preco_mao_de_obra', Numeric(precision=10, scale=2), nullable=False, default=0)
    descricao = Column('descricao', String(1000), nullable=True)
    imagem = Column('imagem', String(300), nullable=True)
    data_cadastro = Column('data_cadastro', DateTime(timezone=False), nullable=False, server_default=func.now(),
                           default=func.now())
    data_atualizacao = Column('data_atualizacao', DateTime(timezone=False), onupdate=func.now())
    responsavel_cadastro_id = Column('responsavel_cadastro_id', Integer)
    detalhes_opcionais = Column('detalhes_opcionais', String(500))
    status = Column('status', Boolean, nullable=False, default=True)
    data_exclusao = Column('data_exclusao', DateTime)
    empresa_id = Column('empresa_id', Integer, ForeignKey('empresa.empresa_id'), nullable=False)


class ServicoBaseModel(BaseModel):
    servico_id: int
    titulo: constr(max_length=500)
    preco_mao_de_obra: float
    descricao: Optional[constr(max_length=1000)]
    imagem: Optional[str]
    data_cadastro: datetime
    data_atualizacao: Optional[datetime]
    detalhes_opcionais: Optional[constr(max_length=500)]
    status: bool
    empresa_id: int
    responsavel_cadastro_id: int
    data_exclusao: Optional[datetime]

    @field_validator('data_cadastro', 'data_atualizacao', 'data_exclusao')
    def format_datetime(cls, value):
        return format_datetime(value)

    class Config:
        from_attributes = True

class ServicoRequestModel(BaseModel):
    titulo: constr(max_length=500)
    preco_mao_de_obra: float
    descricao: Optional[constr(max_length=1000)]
    imagem: Optional[str]
    detalhes_opcionais: Optional[constr(max_length=500)]
    servico_tipo_id: int
    empresa_id: int


