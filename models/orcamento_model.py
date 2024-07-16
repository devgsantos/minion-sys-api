from sqlalchemy import Column, Integer, Boolean, TIMESTAMP, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from datetime import datetime

from .base import Base
from .soft_delete import SoftDeleteQuery
from .datetime_fortaleza_local import fortaleza_now


class OrcamentoModel(Base, SoftDeleteQuery):
    __tablename__ = 'orcamento'

    orcamento_id = Column('orcamento_id', Integer, primary_key=True)
    cliente_id = Column('cliente_id', Integer, ForeignKey('cliente.cliente_id'))
    data_cadastro = Column('data_cadastro', DateTime, default=fortaleza_now, nullable=False)
    data_atualizacao = Column('data_atualizacao', DateTime, nullable=True)
    finalizado = Column('finalizado', Boolean, nullable=False)
    delet = Column('delet', Boolean, nullable=False)
    data_exclusao = Column('data_exclusao', DateTime, nullable=True, default=None)

    cliente = relationship('cliente')
    orcamento_itens = relationship('orcamento_item', back_populates='orcamento')


class OrcamentoBase(BaseModel):
    ClienteId: int
    Data: datetime
    Finalizado: bool

class OrcamentoCreate(OrcamentoBase):
    pass

class Orcamento(OrcamentoBase):
    OrcamentoId: int
