from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base
from .soft_delete import SoftDeleteQuery
from .datetime_fortaleza_local import fortaleza_now


class ProdutoCategoriaModel(Base, SoftDeleteQuery):
    __tablename__ = 'produto_categoria'
    produto_categoria_id = Column('produto_categoria_id', Integer, primary_key=True)
    titulo = Column('titulo', String(300))
    descricao = Column('descricao', String(500))
    sigla = Column('sigla', String(3))
    imagem = Column('imagem', String(300))
    data_cadastro = Column('data_cadastro', DateTime, default=fortaleza_now)
    data_atualizacao = Column('data_atualizacao', DateTime)
    usuario_id = Column('responsavel_cadastro', Integer, ForeignKey('usuario.usuario_id'))
    status = Column('status', Boolean)
    data_exclusao = Column('data_exclusao', DateTime)

    usuario = relationship('Usuario')  # Assuming Usuario is another model

    produtos = relationship('produto', back_populates='produto_categoria')


class ProdutoCategoriaSchema(BaseModel):
    Titulo: str
    Descricao: str
    Imagem: Optional[str] = None
    DataCadastro: datetime
    ResponsavelCadastro: str
    Status: bool

class ProdutoCategoriaCreate(ProdutoCategoriaSchema):
    pass

class ProdutoCategoria(ProdutoCategoriaSchema):
    ProdutoCategoriaId: int

