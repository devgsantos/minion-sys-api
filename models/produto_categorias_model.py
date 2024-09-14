from datetime import datetime
from typing import Optional

from pydantic import BaseModel, constr, field_validator
from sqlalchemy import Column, func,  Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from models.base import Base
from .soft_delete import SoftDeleteQuery
from app.shared.helpers.validators import format_datetime
from .datetime_fortaleza_local import fortaleza_now


class ProdutoCategoriaModel(Base, SoftDeleteQuery):
    __tablename__ = 'produto_categoria'
    produto_categoria_id = Column('produto_categoria_id', Integer, primary_key=True)
    titulo = Column('titulo', String(300), nullable=False)
    descricao = Column('descricao', String(500))
    sigla = Column('sigla', String(3), nullable=False)
    imagem = Column('imagem', String(300))
    data_cadastro = Column('data_cadastro', DateTime(timezone=False), default=func.now())
    data_atualizacao = Column('data_atualizacao', DateTime(timezone=False), onupdate=func.now())
    responsavel_cadastro_id = Column('responsavel_cadastro_id', Integer)
    status = Column('status', Boolean, default=True)
    data_exclusao = Column('data_exclusao', DateTime)

    # produtos = relationship('ProdutoModel', back_populates='produto_categoria')


class ProdutoCategoriaBaseModel(BaseModel):
    produto_categoria_id: int
    titulo: Optional[constr(max_length=300)]
    descricao: Optional[constr(max_length=500)]
    sigla: Optional[constr(max_length=3)]
    imagem: Optional[str]
    data_cadastro: Optional[datetime]
    data_atualizacao: Optional[datetime]
    responsavel_cadastro_id: int
    status: Optional[bool]
    data_exclusao: Optional[datetime]

    @field_validator('data_cadastro', 'data_atualizacao', 'data_exclusao')
    def format_datetime(cls, value):
        return format_datetime(value)

    class Config:
        from_attributes = True


class ProdutoCategoriaRequestModel(BaseModel):
    titulo: constr(max_length=300)
    descricao: Optional[constr(max_length=500)]
    imagem: Optional[str]
