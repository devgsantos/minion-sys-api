from sqlalchemy import Column, func,  Integer, ForeignKey, Boolean, TIMESTAMP, DateTime
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from datetime import datetime

from .base import Base
from .soft_delete import SoftDeleteQuery
from .datetime_fortaleza_local import fortaleza_now
from typing import Optional
from pydantic import BaseModel


class OrcamentoItemModel(Base, SoftDeleteQuery):
    __tablename__ = 'orcamento_item'

    orcamento_item_id = Column('orcamento_item_id', Integer, primary_key=True)
    orcamento_id = Column('orcamento_id', Integer, ForeignKey('orcamento.orcamento_id'))
    produto_id = Column('produto_id', Integer, ForeignKey('produto.produto_id'))
    data_cadastro = Column('data_cadastro', DateTime(timezone=False), default=func.current_timestamp(), nullable=False)
    data_atualizacao = Column('data_atualizacao', DateTime(timezone=False), nullable=True)
    quantidade_orcamento = Column('quantidade_orcamento', Integer, nullable=False)
    finalizado = Column('finalizado', Boolean, nullable=False)
    delet = Column('delet', Boolean, nullable=False)
    data_exclusao = Column('data_exclusao', DateTime(timezone=False), nullable=True, default=None)

    orcamento = relationship('OrcamentoModel', back_populates='orcamento_itens')
    produto = relationship('ProdutoModel')

class OrcamentoItemBaseModel(BaseModel):
    orcamento_item_id: int
    orcamento_id: Optional[int]
    produto_id: Optional[int]
    data_cadastro: datetime
    data_atualizacao: Optional[datetime]
    quantidade_orcamento: int
    finalizado: bool
    delet: bool
    data_exclusao: Optional[datetime]

    class Config:
        orm_mode = True