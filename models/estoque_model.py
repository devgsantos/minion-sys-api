from datetime import datetime

from pydantic import BaseModel
from sqlalchemy import Column, Integer, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship, sessionmaker, scoped_session

from .base import Base
from models.soft_delete import SoftDeleteQuery
from .datetime_fortaleza_local import fortaleza_now


class EstoqueModel(Base, SoftDeleteQuery):
    __tablename__ = 'estoque'
    estoque_id = Column('estoque_id', Integer, primary_key=True)
    produto_id = Column('produto_id', Integer, ForeignKey('produto.produto_id'), nullable=False)
    quantidade_disponivel = Column('quantidade_disponivel', Integer, nullable=False)
    data_cadastro = Column('data_cadastro', DateTime, default=fortaleza_now, nullable=False)
    data_atualizacao = Column('data_atualizacao', DateTime, nullable=True)
    data_exclusao = Column('data_exclusao', DateTime, nullable=True, default=None)

    produto = relationship('produto', back_populates='estoques')

class EstoqueBase(BaseModel):
    ProdutoId: int
    QuantidadeDisponivel: int

class EstoqueCreate(EstoqueBase):
    pass

class Estoque(EstoqueBase):
    EstoqueId: int
