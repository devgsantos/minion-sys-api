from datetime import datetime
from typing import Optional

from pydantic import BaseModel, condecimal, constr
from sqlalchemy import Column, func,  Integer, String, Numeric, ForeignKey, DateTime, Boolean, Float
from sqlalchemy.orm import relationship, scoped_session, sessionmaker
from .base import Base
from .soft_delete import SoftDeleteQuery
from .datetime_fortaleza_local import fortaleza_now


class ProdutoModel(Base, SoftDeleteQuery):
    __tablename__ = 'produto'
    produto_id = Column('produto_id', Integer, primary_key=True)
    titulo = Column('titulo', String(500), nullable=False)
    preco = Column('preco', Numeric(precision=10, scale=2), nullable=False)
    descricao = Column('descricao', String(1000))
    imagem = Column('imagem', String(300))
    data_cadastro = Column('data_cadastro', DateTime(timezone=False), nullable=False, default=func.current_timestamp())
    data_atualizacao = Column('data_atualizacao', DateTime)
    responsavel_cadastro = Column('responsavel_cadastro', String(300))
    detalhes_opcionais = Column('detalhes_opcionais', String(500))
    status = Column('status', Boolean, nullable=False)
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
    empresa = relationship('EmpresaModel')

class ProdutoBaseModel(BaseModel):
    produto_id: int
    titulo: constr(max_length=500)
    preco: condecimal(max_digits=10, decimal_places=2)
    descricao: Optional[constr(max_length=1000)]
    imagem: Optional[str]
    data_cadastro: datetime
    data_atualizacao: Optional[datetime]
    responsavel_cadastro: Optional[constr(max_length=300)]
    detalhes_opcionais: Optional[constr(max_length=500)]
    status: bool
    data_exclusao: Optional[datetime]
    produto_categoria_id: int
    produto_subcategoria_id: int
    produto_tipo_id: int
    empresa_id: int

    class Config:
        orm_mode = True