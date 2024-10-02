from sqlalchemy import Column, func, Integer, Boolean, ForeignKey, DateTime, Numeric
from sqlalchemy.orm import relationship
from pydantic import BaseModel, field_validator
from typing import Optional

from datetime import datetime

from app.shared.helpers.validators import format_datetime
from models.base import Base
from .soft_delete import SoftDeleteQuery



class OrcamentoModel(Base, SoftDeleteQuery):
    __tablename__ = 'orcamento'

    orcamento_id = Column('orcamento_id', Integer, primary_key=True)
    cliente_id = Column('cliente_id', Integer, ForeignKey('cliente.cliente_id'))
    empresa_id = Column('empresa_id', Integer, ForeignKey('empresa.empresa_id'))
    valor = Column('valor', Numeric(precision=10, scale=2), nullable=False, default=0)
    desconto = Column('desconto', Numeric(precision=10, scale=2), nullable=False, default=0)
    data_cadastro = Column('data_cadastro', DateTime(timezone=False), default=func.now(), nullable=False)
    data_atualizacao = Column('data_atualizacao', DateTime(timezone=False), onupdate=func.now())
    orcamento_status_id = Column('orcamento_status_id', Integer, ForeignKey('orcamento_status.orcamento_status_id'))
    orcamento_tipo_id = Column('orcamento_tipo_id', Integer, ForeignKey('orcamento_tipo.orcamento_tipo_id'))
    data_exclusao = Column('data_exclusao', DateTime(timezone=False), nullable=True, default=None)

    cliente = relationship('ClienteModel')
    empresa = relationship('EmpresaModel')
    orcamento_status = relationship('OrcamentoStatusModel')
    orcamento_tipo = relationship('OrcamentoTipoModel')
    orcamento_itens = relationship('OrcamentoItemModel', cascade='all')

class OrcamentoBaseModel(BaseModel):
    orcamento_id: int
    cliente_id: Optional[int]
    data_cadastro: datetime
    data_atualizacao: Optional[datetime]
    finalizado: bool
    delet: bool
    data_exclusao: Optional[datetime]

    @field_validator('data_cadastro', 'data_atualizacao', 'data_exclusao')
    def format_datetime(cls, value):
        return format_datetime(value)

    class Config:
        from_attributes = True