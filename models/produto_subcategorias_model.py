from datetime import datetime

from pydantic import BaseModel, constr
from sqlalchemy import Column, func,  Integer, String, Numeric, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from models.base import Base
from typing import List, Optional

from .soft_delete import SoftDeleteQuery
from .datetime_fortaleza_local import fortaleza_now


class ProdutoSubcategoriaModel(Base, SoftDeleteQuery):
    __tablename__ = 'produto_subcategoria'

    produto_sub_categoria_id = Column('produto_subcategoria_id', Integer, primary_key=True)
    titulo = Column('titulo', String(300))
    descricao = Column('descricao', String(500))
    imagem = Column('imagem', String(300))
    data_cadastro = Column('data_cadastro', DateTime(timezone=False), nullable=False, server_default=func.now(), default=func.now())
    data_atualizacao = Column('data_atualizacao', DateTime, onupdate=func.now())
    responsavel_cadastro_id = Column('responsavel_cadastro_id', Integer)
    status = Column('status', Boolean)
    data_exclusao = Column('data_exclusao', DateTime)
    usuario_id = Column('usuario_id', Integer, ForeignKey('usuario.usuario_id'))

    produtos = relationship('ProdutoModel', back_populates='produto_subcategoria')

class ProdutoSubcategoriaBaseModel(BaseModel):
    produto_sub_categoria_id: int
    titulo: Optional[constr(max_length=300)]
    descricao: Optional[constr(max_length=500)]
    imagem: Optional[str]
    data_cadastro: datetime
    data_atualizacao: Optional[datetime]
    responsavel_cadastro: Optional[constr(max_length=100)]
    status: Optional[bool]
    data_exclusao: Optional[datetime]
    usuario_id: Optional[int]

    class Config:
        orm_mode = True