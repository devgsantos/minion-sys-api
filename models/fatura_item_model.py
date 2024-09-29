from sqlalchemy import Column, func,  Integer, ForeignKey, Boolean, TIMESTAMP, DateTime
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from datetime import datetime

from models.base import Base
from .soft_delete import SoftDeleteQuery
from .datetime_fortaleza_local import fortaleza_now
from typing import Optional


class FaturaItemModel(Base, SoftDeleteQuery):
    __tablename__ = 'fatura_item'

    fatura_item_id = Column('fatura_item_id', Integer, primary_key=True)
    fatura_id = Column('fatura_id', Integer, ForeignKey('fatura.fatura_id'), nullable=False)
    produto_id = Column('produto_id', Integer, ForeignKey('produto.produto_id'), nullable=False)
    data_cadastro = Column('data_cadastro', DateTime(timezone=False), default=func.now(), nullable=False)
    data_atualizacao = Column('data_atualizacao', DateTime(timezone=False), onupdate=func.now())
    quantidade_faturada = Column('quantidade_faturada', Integer, nullable=False)
    data_exclusao = Column('data_exclusao', DateTime(timezone=False), nullable=True, default=None)

    fatura = relationship('FaturaModel', back_populates='fatura_itens')
    produto = relationship('ProdutoModel')

class FaturaItemBaseModel(BaseModel):
    fatura_item_id: int
    fatura_id: int
    produto_id: int
    data_cadastro: datetime
    data_atualizacao: Optional[datetime]
    quantidade_faturada: int
    data_exclusao: Optional[datetime]

    class Config:
        from_attibutes = True