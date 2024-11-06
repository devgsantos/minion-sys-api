from datetime import datetime

from pydantic import BaseModel, field_validator
from sqlalchemy import Column, func, Integer, ForeignKey, DateTime, Numeric, Boolean
from sqlalchemy.orm import relationship

from models import OrcamentoBaseModel
from models.base import Base
from models.soft_delete import SoftDeleteQuery
from typing import Optional
from app.shared.helpers.validators import format_datetime
from models.venda_status_model import VendaStatusBaseModel


class VendaModel(Base, SoftDeleteQuery):
    __tablename__ = 'venda'
    venda_id = Column('venda_id', Integer, primary_key=True)
    venda_status_id = Column('venda_status_id', Integer, ForeignKey('venda_status.venda_status_id'))
    orcamento_id = Column('orcamento_id', Integer, ForeignKey('orcamento.orcamento_id'), nullable=False)
    valor = Column('valor', Numeric(precision=10, scale=2), nullable=False, default=0)
    gera_ordem_servico = Column('gera_ordem_servico', Boolean, nullable=False, default=False)
    empresa_id = Column('empresa_id', Integer, ForeignKey('empresa.empresa_id'), nullable=False)
    responsavel_cadastro_id = Column('responsavel_cadastro_id', Integer)
    data_cadastro = Column('data_cadastro', DateTime(timezone=False), default=func.now(), nullable=False)
    data_atualizacao = Column('data_atualizacao', DateTime(timezone=False), onupdate=func.now())
    data_exclusao = Column('data_exclusao', DateTime(timezone=False), nullable=True)

    orcamento = relationship("OrcamentoModel", foreign_keys=[orcamento_id])
    venda_status = relationship('VendaStatusModel')
    empresa = relationship('EmpresaModel')


class VendaBaseModel(BaseModel):
    venda_id: int
    orcamento_id: int
    empresa_id: int
    data_cadastro: datetime
    data_atualizacao: Optional[datetime]

    venda_status: Optional[VendaStatusBaseModel]
    orcamento: OrcamentoBaseModel

    @field_validator('data_cadastro', 'data_atualizacao')
    def format_datetime(cls, value):
        return format_datetime(value)

    class Config:
        from_attributes = True

class VendaRequestBaseModel(BaseModel):
    orcamento_id: int
    empresa_id: int
    venda_status_id: Optional[int]
    gera_ordem_servico: bool = False

    class Config:
        from_attributes = True
