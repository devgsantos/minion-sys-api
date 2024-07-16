from sqlalchemy import Column, Integer, ForeignKey, Boolean, TIMESTAMP, DateTime
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from datetime import datetime

from .base import Base
from .soft_delete import SoftDeleteQuery
from .datetime_fortaleza_local import fortaleza_now


class FaturaModel(Base, SoftDeleteQuery):
    __tablename__ = 'fatura'

    fatura_id = Column('fatura_id', Integer, primary_key=True)
    orcamento_id = Column('orcamento_id', Integer, ForeignKey('orcamento.orcamento_id'), nullable=False)
    cliente_id = Column('cliente_id', Integer, ForeignKey('cliente.cliente_id'), nullable=False)
    data_cadastro = Column('data_cadastro', DateTime, default=fortaleza_now, nullable=False)
    status_entrega = Column('status_entrega', Integer, nullable=False)
    delet = Column('delet', Boolean, nullable=False)
    data_exclusao = Column('data_exclusao', DateTime, nullable=True, default=None)

    cliente = relationship('cliente', back_populates='faturas')
    orcamento = relationship('orcamento', back_populates='fatura')
    fatura_itens = relationship('faturaIItem', back_populates='fatura')


class FaturaBase(BaseModel):
    OrcamentoId: int
    ClienteId: int
    Data: datetime
    StatusEntrega: int

class FaturaCreate(FaturaBase):
    pass

class Fatura(FaturaBase):
    FaturaId: int
