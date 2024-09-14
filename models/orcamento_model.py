from sqlalchemy import Column, func,  Integer, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from typing import Optional

from datetime import datetime

from models.base import Base
from .soft_delete import SoftDeleteQuery
from .datetime_fortaleza_local import fortaleza_now



class OrcamentoModel(Base, SoftDeleteQuery):
    __tablename__ = 'orcamento'

    orcamento_id = Column('orcamento_id', Integer, primary_key=True)
    cliente_id = Column('cliente_id', Integer, ForeignKey('cliente.cliente_id'))
    data_cadastro = Column('data_cadastro', DateTime(timezone=False), default=func.now(), nullable=False)
    data_atualizacao = Column('data_atualizacao', DateTime(timezone=False), onupdate=func.now())
    finalizado = Column('finalizado', Boolean, nullable=False)
    data_exclusao = Column('data_exclusao', DateTime(timezone=False), nullable=True, default=None)

    cliente = relationship('ClienteModel')
    orcamento_itens = relationship('OrcamentoItemModel', back_populates='orcamento')

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