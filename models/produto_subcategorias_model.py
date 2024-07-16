from datetime import datetime

from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from .base import Base
from typing import List, Optional

from .soft_delete import SoftDeleteQuery
from .datetime_fortaleza_local import fortaleza_now


class ProdutoSubategoriaModel(Base, SoftDeleteQuery):
    __tablename__ = 'produto_subcategoria'

    produto_sub_categoria_id = Column('produto_subcategoria_id', Integer, primary_key=True)
    titulo = Column('titulo', String(300))
    descricao = Column('descricao', String(500))
    imagem = Column('imagem', String(300))
    data_cadastro = Column('data_cadastro', DateTime, nullable=False, default=fortaleza_now)
    data_atualizacao = Column('data_atualizacao', DateTime)
    responsavel_cadastro = Column('responsavel_cadastro', String(100))
    status = Column('status', Boolean)
    data_exclusao = Column('data_exclusao', DateTime)
    usuario_id = Column('usuario_id', Integer, ForeignKey('usuario.usuario_id'))

    usuario = relationship('usuario')
    produtos = relationship('produto', backref='produto_subcategoria')

class ProdutoSubCategoriaSchema(BaseModel):
    Titulo: str
    Descricao: str
    Imagem: Optional[str] = None
    DataCadastro: datetime
    ResponsavelCadastro: str
    Status: bool

class ProdutoSubCategoriaCreate(ProdutoSubCategoriaSchema):
    pass

class ProdutoSubCategoria(ProdutoSubCategoriaSchema):
    ProdutoSubCategoriaId: int
