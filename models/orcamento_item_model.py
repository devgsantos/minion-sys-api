from sqlalchemy import Column, func,  Integer, ForeignKey, Boolean, TIMESTAMP, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from pydantic import BaseModel, field_validator
from datetime import datetime

from app.shared.helpers.validators import format_datetime
from models.base import Base
from .soft_delete import SoftDeleteQuery
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
    quantidade_orcamento = Column('quantidade_orcamento', Integer)
    data_exclusao = Column('data_exclusao', DateTime(timezone=False), nullable=True, default=None)

    produto = relationship('ProdutoModel')
    servico = relationship('ServicoModel')

    @hybrid_property
    def titulo(self):
        """Retorna o título do produto se existir produto_id, senão retorna None"""
        if self.produto:
            return self.produto.titulo
        # Se houver serviço, você pode retornar o título do serviço também
        elif self.servico and hasattr(self.servico, 'titulo'):
            return self.servico.titulo
        return None

    @hybrid_property
    def sku(self):
        """Retorna o SKU do produto se existir produto_id, senão retorna None"""
        if self.produto and hasattr(self.produto, 'sku'):
            return self.produto.sku
        return None

class OrcamentoItemBaseModel(BaseModel):
    servico_id: Optional[int]
    produto_id: Optional[int]
    titulo: Optional[str] = None  # Agora é opcional e vem da relação com produto/serviço
    sku: Optional[str] = None  # SKU do produto relacionado
    quantidade_orcamento: int

    class Config:
        from_attributes = True