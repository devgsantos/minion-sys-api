from datetime import datetime

from pydantic import BaseModel
from sqlalchemy import Column, func,  Integer, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship, sessionmaker, scoped_session

from .base import Base
from models.soft_delete import SoftDeleteQuery
from .datetime_fortaleza_local import fortaleza_now
from typing import Optional


class EstoqueModel(Base, SoftDeleteQuery):
    __tablename__ = 'estoque'
    estoque_id = Column('estoque_id', Integer, primary_key=True)
    produto_id = Column('produto_id', Integer, ForeignKey('produto.produto_id'), nullable=False)
    quantidade_disponivel = Column('quantidade_disponivel', Integer, nullable=False)
    data_cadastro = Column('data_cadastro, DateTime(timezone=False), default=func.current_timestamp(), nullable=False)
    data_atualizacao = Column('data_atualizacao, DateTime(timezone=False), nullable=True)
    data_exclusao = Column('data_exclusao, DateTime(timezone=False), nullable=True, default=None)

    produto = relationship('produto', back_populates='estoques')

class EstoqueBaseModel(BaseModel):
    estoque_id: int
    produto_id: int
    quantidade_disponivel: int
    data_cadastro: datetime
    data_atualizacao: Optional[datetime]
    data_exclusao: Optional[datetime]

    class Config:
        orm_mode = True