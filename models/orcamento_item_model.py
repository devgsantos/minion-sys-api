from sqlalchemy import Column, func,  Integer, ForeignKey, Boolean, TIMESTAMP, DateTime
from sqlalchemy.orm import relationship
from pydantic import BaseModel, field_validator
from datetime import datetime

from app.shared.helpers.validators import format_datetime
from models.base import Base
from .soft_delete import SoftDeleteQuery
from .datetime_fortaleza_local import fortaleza_now
from typing import Optional
from pydantic import BaseModel


class OrcamentoItemModel(Base, SoftDeleteQuery):
    __tablename__ = 'orcamento_item'

    orcamento_item_id = Column('orcamento_item_id', Integer, primary_key=True)
    orcamento_id = Column('orcamento_id', Integer, ForeignKey('orcamento.orcamento_id'))
    produto_id = Column('produto_id', Integer, ForeignKey('produto.produto_id'))
    servico_id = Column('servico_id', Integer, ForeignKey('servico.servico_id'))
    data_cadastro = Column('data_cadastro', DateTime(timezone=False), default=func.now(), nullable=False)
    data_atualizacao = Column('data_atualizacao', DateTime(timezone=False), onupdate=func.now())
    quantidade_orcamento = Column('quantidade_orcamento', Integer, nullable=False)
    data_exclusao = Column('data_exclusao', DateTime(timezone=False), nullable=True, default=None)

    produto = relationship('ProdutoModel')

class OrcamentoItemBaseModel(BaseModel):
    orcamento_id: Optional[int]
    quantidade_orcamento: int
    finalizado: bool
    data_cadastro: Optional[datetime]

    @field_validator('data_cadastro', 'data_atualizacao', 'data_exclusao')
    def format_datetime(cls, value):
        return format_datetime(value)

    class Config:
        from_attributes = True