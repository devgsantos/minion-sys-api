from typing import Optional

from sqlalchemy import Column, func,  Integer, ForeignKey, Boolean, TIMESTAMP, DateTime
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from datetime import datetime

from models.base import Base
from .soft_delete import SoftDeleteQuery
from .datetime_fortaleza_local import fortaleza_now
from pydantic import BaseModel


class FaturaModel(Base, SoftDeleteQuery):
    __tablename__ = 'fatura'

    fatura_id = Column('fatura_id', Integer, primary_key=True)
    orcamento_id = Column('orcamento_id', Integer, ForeignKey('orcamento.orcamento_id'), nullable=False)
    cliente_id = Column('cliente_id', Integer, ForeignKey('cliente.cliente_id'), nullable=False)
    data_cadastro = Column('data_cadastro', DateTime(timezone=False), default=func.now(), nullable=False)
    status_entrega = Column('status_entrega', Integer, nullable=False)
    delet = Column('delet', Boolean, nullable=False)
    data_exclusao = Column('data_exclusao', DateTime(timezone=False), nullable=True, default=None)

    cliente = relationship('ClienteModel')
    orcamento = relationship('OrcamentoModel')
    fatura_itens = relationship('FaturaItemModel', back_populates='fatura')

class FaturaBaseModel(BaseModel):
    fatura_id: int
    orcamento_id: int
    cliente_id: int
    data_cadastro: datetime
    status_entrega: int
    delet: bool
    data_exclusao: Optional[datetime]

    class Config:
        from_attibutes = True