from sqlalchemy import Column, Integer, ForeignKey, Boolean, TIMESTAMP, DateTime
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from datetime import datetime

from .base import Base
from .soft_delete import SoftDeleteQuery
from .datetime_fortaleza_local import fortaleza_now


class OrcamentoItemModel(Base, SoftDeleteQuery):
    __tablename__ = 'orcamento_item'

    orcamento_item_id = Column('orcamento_item_id', Integer, primary_key=True)
    orcamento_id = Column('orcamento_id', Integer, ForeignKey('orcamento.orcamento_id'))
    produto_id = Column('produto_id', Integer, ForeignKey('produto.produto_id'))
    data_cadastro = Column('data_cadastro', DateTime, default=fortaleza_now, nullable=False)
    data_atualizacao = Column('data_atualizacao', DateTime, nullable=True)
    quantidade_orcamento = Column('quantidade_orcamento', Integer, nullable=False)
    finalizado = Column('finalizado', Boolean, nullable=False)
    delet = Column('delet', Boolean, nullable=False)
    data_exclusao = Column('data_exclusao', DateTime, nullable=True, default=None)

    orcamento = relationship('orcamento', back_populates='orcamento_itens')
    produto = relationship('produto')
class OrcamentoItemSchema(BaseModel):
    OrcamentoId: int
    Data: datetime
    QuantidadeOrcamento: int
    Finalizado: bool

class OrcamentoItemCreate(OrcamentoItemSchema):
    pass

class OrcamentoItem(OrcamentoItemSchema):
    OrcamentoItemId: int
