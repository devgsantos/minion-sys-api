from datetime import datetime

from pydantic import BaseModel, constr, field_validator
from sqlalchemy import Column, func,  Integer, String, Numeric, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from models.base import Base
from typing import List, Optional
from app.shared.helpers.validators import format_datetime
from .produto_categorias_model import ProdutoCategoriaBaseModel
from .soft_delete import SoftDeleteQuery
from .datetime_fortaleza_local import fortaleza_now


class ProdutoSubcategoriaModel(Base, SoftDeleteQuery):
    __tablename__ = 'produto_subcategoria'

    produto_sub_categoria_id = Column('produto_subcategoria_id', Integer, primary_key=True)
    titulo = Column('titulo', String(300), nullable=False)
    descricao = Column('descricao', String(500))
    imagem = Column('imagem', String(300))
    sigla = Column('sigla', String(3), nullable=False)
    data_cadastro = Column('data_cadastro', DateTime(timezone=False), nullable=False, server_default=func.now(), default=func.now())
    data_atualizacao = Column('data_atualizacao', DateTime, onupdate=func.now())
    responsavel_cadastro_id = Column('responsavel_cadastro_id', Integer)
    produto_categoria_id = Column('produto_categoria_id', Integer, ForeignKey('produto_categoria.produto_categoria_id'))
    status = Column('status', Boolean, default=True)
    data_exclusao = Column('data_exclusao', DateTime)

    categoria = relationship('ProdutoCategoriaModel')

class ProdutoSubcategoriaBaseModel(BaseModel):
    produto_sub_categoria_id: int
    titulo: Optional[constr(max_length=300)]
    descricao: Optional[constr(max_length=500)]
    imagem: Optional[str]
    sigla: Optional[str]
    data_cadastro: datetime
    data_atualizacao: Optional[datetime]
    responsavel_cadastro_id: int
    status: Optional[bool]
    data_exclusao: Optional[datetime]

    @field_validator('data_cadastro', 'data_atualizacao', 'data_exclusao')
    def format_datetime(cls, value):
        return format_datetime(value)

    class Config:
        from_attributes = True