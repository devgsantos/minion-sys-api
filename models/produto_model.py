from datetime import datetime
from typing import Optional, List

from _decimal import Decimal
from pydantic import BaseModel, condecimal, constr, field_validator
from sqlalchemy import Column, func,  Integer, String, Numeric, ForeignKey, DateTime, Boolean, Float
from sqlalchemy.orm import relationship, scoped_session, sessionmaker
from models.base import Base
from .estoque_model import EstoqueBaseModel, EstoqueProdutoBaseModel
from .produto_categorias_model import ProdutoCategoriaBaseModel
from .produto_subcategorias_model import ProdutoSubcategoriaBaseModel
from .produto_tipos_model import ProdutoTipoBaseModel
from .soft_delete import SoftDeleteQuery
from app.shared.helpers.validators import format_datetime


class ProdutoModel(Base, SoftDeleteQuery):
    __tablename__ = 'produto'
    produto_id = Column('produto_id', Integer, primary_key=True)
    titulo = Column('titulo', String(500), nullable=False)
    sku = Column('sku', String(13), nullable=True)
    preco_venda = Column('preco_venda', Numeric(precision=10, scale=2), nullable=False, default=0)
    preco_custo = Column('preco_custo', Numeric(precision=10, scale=2), nullable=False, default=0)
    descricao = Column('descricao', String(1000), nullable=True)
    imagem = Column('imagem', String(300), nullable=True)
    data_cadastro = Column('data_cadastro', DateTime(timezone=False), nullable=False, server_default=func.now(),
                           default=func.now())
    data_atualizacao = Column('data_atualizacao', DateTime(timezone=False), onupdate=func.now())
    responsavel_cadastro_id = Column('responsavel_cadastro_id', Integer)
    detalhes_opcionais = Column('detalhes_opcionais', String(500))
    status = Column('status', Boolean, nullable=False, default=True)
    data_exclusao = Column('data_exclusao', DateTime)
    produto_categoria_id = Column('produto_categoria_id', Integer, ForeignKey('produto_categoria.produto_categoria_id'),
                                  nullable=False)
    produto_subcategoria_id = Column('produto_subcategoria_id', Integer,
                                     ForeignKey('produto_subcategoria.produto_subcategoria_id'), nullable=False)
    produto_tipo_id = Column('produto_tipo_id', Integer, ForeignKey('produto_tipo.produto_tipo_id'), nullable=False)
    empresa_id = Column('empresa_id', Integer, ForeignKey('empresa.empresa_id'), nullable=False)

    produto_categoria = relationship('ProdutoCategoriaModel')
    produto_subcategoria = relationship('ProdutoSubcategoriaModel')
    produto_tipo = relationship('ProdutoTipoModel')
    estoque = relationship("EstoqueModel", back_populates="produto", cascade="all, delete-orphan")

class ProdutoBaseModel(BaseModel):
    produto_id: int
    titulo: constr(max_length=500)
    preco_custo: float
    preco_venda: float
    descricao: Optional[constr(max_length=1000)]
    imagem: Optional[str]
    sku: Optional[str]
    data_cadastro: datetime
    data_atualizacao: Optional[datetime]
    detalhes_opcionais: Optional[constr(max_length=500)]
    status: bool
    empresa_id: int
    responsavel_cadastro_id: int
    data_exclusao: Optional[datetime]

    produto_categoria: Optional[ProdutoCategoriaBaseModel]
    produto_subcategoria: Optional[ProdutoSubcategoriaBaseModel]
    produto_tipo: Optional[ProdutoTipoBaseModel]
    estoque: Optional[List[EstoqueBaseModel]]

    @field_validator('data_cadastro', 'data_atualizacao', 'data_exclusao')
    def format_datetime(cls, value):
        return format_datetime(value)

    class Config:
        from_attributes = True

class ProdutoRelBaseModel(BaseModel):
    produto_id: int
    titulo: constr(max_length=500)
    sku: Optional[str]
    preco_custo: float
    preco_venda: float
    descricao: Optional[constr(max_length=1000)]
    imagem: Optional[str]
    empresa_id: int
    status: int

    estoque: Optional[List[EstoqueBaseModel]]

    class Config:
        from_attributes = True


class ProdutoRequestModel(BaseModel):
    titulo: constr(max_length=500)
    preco_custo: float
    preco_venda: float
    descricao: Optional[constr(max_length=1000)]
    imagem: Optional[str]
    detalhes_opcionais: Optional[constr(max_length=500)]
    produto_categoria_id: int
    produto_subcategoria_id: int
    produto_tipo_id: int
    empresa_id: int
    estoque: Optional[List[EstoqueProdutoBaseModel]]

    class Config:
        from_attributes = True

