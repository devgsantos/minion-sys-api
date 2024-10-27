from sqlalchemy import Column, func, Integer, Boolean, ForeignKey, DateTime, Numeric
from sqlalchemy.orm import relationship
from pydantic import BaseModel, field_validator, model_validator, Field
from typing import Optional, List, Union

from datetime import datetime

from app.shared.helpers.validators import format_datetime
from models.base import Base
from .orcamento_item_model import OrcamentoItemBaseModel
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
    responsavel_cadastro_id = Column('responsavel_cadastro_id', Integer)
    orcamento_status_id = Column('orcamento_status_id', Integer, ForeignKey('orcamento_status.orcamento_status_id'))
    orcamento_tipo_id = Column('orcamento_tipo_id', Integer)
    data_exclusao = Column('data_exclusao', DateTime(timezone=False), nullable=True, default=None)

    cliente = relationship('ClienteModel')
    empresa = relationship('EmpresaModel')
    orcamento_status = relationship('OrcamentoStatusModel')
    orcamento_itens = relationship('OrcamentoItemModel')

class OrcamentoBaseModel(BaseModel):
    orcamento_id: int
    cliente_id: Optional[int]
    data_cadastro: datetime
    data_atualizacao: Optional[datetime]
    data_exclusao: Optional[datetime]

    orcamento_itens: List[OrcamentoItemBaseModel]

    @field_validator('data_cadastro', 'data_atualizacao', 'data_exclusao')
    def format_datetime(cls, value):
        return format_datetime(value)

    class Config:
        from_attributes = True

class ProdutoItemOrcamentoModel(BaseModel):
    produto_id: int
    quantidade_orcamento: int

class ServicoItemOrcamentoModel(BaseModel):
    servico_id: int
    quantidade_orcamento: int

class OrcamentoRequestModel(BaseModel):
    cliente_id: int
    desconto: float
    empresa_id: int
    orcamento_status_id: int
    orcamento_itens: List[Union[ProdutoItemOrcamentoModel, ServicoItemOrcamentoModel]]

    @model_validator(mode='before')
    def validate_items(cls, values):
        itens = values.get('orcamento_itens')
        if not itens or not isinstance(itens, list):
            raise ValueError("O campo 'orcamento_itens' é obrigatório e deve ser uma lista.")

        for item in itens:
            if not ('produto_id' in item or 'servico_id' in item):
                raise ValueError("Cada item deve ter 'produto_id' ou 'servico_id'.")

        return values
