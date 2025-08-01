from sqlalchemy import Column, func, Integer, ForeignKey, DateTime, Numeric, String, Boolean
from sqlalchemy.orm import relationship
from pydantic import BaseModel, field_validator, model_validator, Field, constr
from typing import Optional, List, Union

from datetime import datetime

from app.shared.helpers.validators import format_datetime
from models.base import Base
from . import ClienteServicoBaseModel
from .orcamento_status_model import OrcamentoStatusBaseModel
from .orcamento_item_model import OrcamentoItemBaseModel
from .soft_delete import SoftDeleteQuery
from app.shared.singletons.logger import Logger




class OrcamentoModel(Base, SoftDeleteQuery):
    __tablename__ = 'orcamento'

    orcamento_id = Column('orcamento_id', Integer, primary_key=True)
    cliente_id = Column('cliente_id', Integer, ForeignKey('cliente.cliente_id'))
    empresa_id = Column('empresa_id', Integer, ForeignKey('empresa.empresa_id'))
    descricao = Column('descricao', String(1000), nullable=True)
    observacoes = Column('observacoes', String(1000))
    valor = Column('valor', Numeric(precision=10, scale=2), nullable=False, default=0)
    desconto = Column('desconto', Numeric(precision=10, scale=2), nullable=False, default=0)
    data_cadastro = Column('data_cadastro', DateTime(timezone=False), default=func.now(), nullable=False)
    data_entrega = Column('data_entrega', DateTime(timezone=False), nullable=True, default=None)
    data_atualizacao = Column('data_atualizacao', DateTime(timezone=False), onupdate=func.now())
    responsavel_cadastro_id = Column('responsavel_cadastro_id', Integer)
    orcamento_status_id = Column('orcamento_status_id', Integer, ForeignKey('orcamento_status.orcamento_status_id'))
    venda_id = Column('venda_id', Integer, ForeignKey('venda.venda_id'), nullable=True)
    data_aprovacao_reprovacao = Column('data_aprovacao', DateTime(timezone=False), nullable=True, default=None)
    data_exclusao = Column('data_exclusao', DateTime(timezone=False), nullable=True, default=None)

    cliente = relationship('ClienteModel')
    venda = relationship('VendaModel', foreign_keys=[venda_id])
    empresa = relationship('EmpresaModel')
    orcamento_status = relationship('OrcamentoStatusModel')
    orcamento_itens = relationship(
        'OrcamentoItemModel',
        primaryjoin='and_(OrcamentoItemModel.orcamento_id == OrcamentoModel.orcamento_id, '
                    'OrcamentoItemModel.data_exclusao.is_(None))',
        lazy='joined'
    )

class OrcamentoBaseModel(BaseModel):
    orcamento_id: int
    cliente_id: Optional[int]
    descricao: Optional[constr(max_length=1000)]
    observacoes: Optional[constr(max_length=1000)]
    data_cadastro: datetime
    data_entrega: Optional[datetime]
    valor: float = Field(default=0, ge=0)
    data_aprovacao_reprovacao: Optional[datetime]
    data_atualizacao: Optional[datetime]
    data_exclusao: Optional[datetime]

    orcamento_itens: List[OrcamentoItemBaseModel]
    orcamento_status: OrcamentoStatusBaseModel
    venda_id: Optional[int]
    cliente: ClienteServicoBaseModel

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

class OrcamentoItensRequest(BaseModel):
    tipo: str
    item_id: int
    quantidade_orcamento: int

class OrcamentoRequestModel(BaseModel):
    orcamento_id: Optional[int] = None
    cliente_id: int
    desconto: float
    empresa_id: int
    data_entrega: Optional[datetime]
    descricao: Optional[constr(max_length=1000)]
    observacoes: Optional[constr(max_length=1000)]
    orcamento_status_id: int
    venda_id: Optional[int] = None
    orcamento_itens: List[
            Union[
                ProdutoItemOrcamentoModel,
                ServicoItemOrcamentoModel,
                OrcamentoItensRequest
            ]
        ]
        

    @model_validator(mode='before')
    def validate_items(cls, values):
        itens = values.get('orcamento_itens')
        if not itens or not isinstance(itens, list):
            Logger().log(message="O campo 'orcamento_itens' é obrigatório e deve ser uma lista.", level='error')
            raise ValueError("O campo 'orcamento_itens' é obrigatório e deve ser uma lista.")

        for item in itens:
            if not ('produto_id' in item or 'servico_id' in item or ('item_id' in item and 'tipo' in item)):
                Logger().log(message="Cada item deve ter 'produto_id' ou 'servico_id' ou especificar o 'tipo'.", level='error')
                raise ValueError("Cada item deve ter 'produto_id' ou 'servico_id' ou especificar o 'tipo'.")

        return values
