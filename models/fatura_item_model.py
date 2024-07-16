from sqlalchemy import Column, Integer, ForeignKey, Boolean, TIMESTAMP, DateTime
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from datetime import datetime

from .base import Base
from .soft_delete import SoftDeleteQuery
from .datetime_fortaleza_local import fortaleza_now


class FaturaItemModel(Base, SoftDeleteQuery):
    __tablename__ = 'fatura_item'

    fatura_item_id = Column('fatura_item_id', Integer, primary_key=True)
    fatura_id = Column('fatura_id', Integer, ForeignKey('fatura.fatura_id'), nullable=False)
    produto_id = Column('produto_id', Integer, ForeignKey('produto.produto_id'), nullable=False)
    data_cadastro = Column('data_cadastro', DateTime, default=fortaleza_now, nullable=False)
    data_atualizacao = Column('data_atualizacao', DateTime, nullable=True)
    quantidade_faturada = Column('quantidade_faturada', Integer, nullable=False)
    data_exclusao = Column('data_exclusao', DateTime, nullable=True, default=None)

    fatura = relationship('fatura', back_populates='fatura_itens')
    produto = relationship('produto')

class FaturaItemBase(BaseModel):
    FaturaId: int
    Data: datetime
    QuantidadeFaturada: int

class FaturaItemCreate(FaturaItemBase):
    pass

class FaturaItem(FaturaItemBase):
    FaturaItemId: int
