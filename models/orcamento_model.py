from sqlalchemy import Column, func,  Integer, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from typing import Optional

from datetime import datetime

from .base import Base
from .soft_delete import SoftDeleteQuery
from .datetime_fortaleza_local import fortaleza_now



class OrcamentoModel(Base, SoftDeleteQuery):
    __tablename__ = 'orcamento'

    orcamento_id = Column('orcamento_id', Integer, primary_key=True)
    cliente_id = Column('cliente_id', Integer, ForeignKey('cliente.cliente_id'))
    data_cadastro = Column('data_cadastro', DateTime(timezone=False), default=func.current_timestamp(), nullable=False)
    data_atualizacao = Column('data_atualizacao', DateTime(timezone=False), nullable=True)
    finalizado = Column('finalizado', Boolean, nullable=False)
    delet = Column('delet', Boolean, nullable=False)
    data_exclusao = Column('data_exclusao', DateTime(timezone=False), nullable=True, default=None)

    cliente = relationship('cliente')
    orcamento_itens = relationship('orcamento_item', back_populates='orcamento')

class OrcamentoBaseModel(BaseModel):
    orcamento_id: int
    cliente_id: Optional[int]
    data_cadastro: datetime
    data_atualizacao: Optional[datetime]
    finalizado: bool
    delet: bool
    data_exclusao: Optional[datetime]

    class Config:
        orm_mode = True