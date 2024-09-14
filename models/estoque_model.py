from datetime import datetime

from pydantic import BaseModel, field_validator
from sqlalchemy import Column, func,  Integer, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship, sessionmaker, scoped_session

from models.base import Base
from models.estoque_tipo_model import EstoqueTipoBaseModel
from models.soft_delete import SoftDeleteQuery
from typing import Optional
from app.shared.helpers.validators import format_datetime



class EstoqueModel(Base, SoftDeleteQuery):
    __tablename__ = 'estoque'
    estoque_id = Column('estoque_id', Integer, primary_key=True)
    produto_id = Column('produto_id', Integer, ForeignKey('produto.produto_id'), nullable=False)
    estoque_tipo_id = Column('estoque_tipo_id', Integer, ForeignKey('estoque_tipo.estoque_tipo_id'), nullable=False)
    quantidade_disponivel = Column('quantidade_disponivel', Integer, nullable=False)
    data_cadastro = Column('data_cadastro', DateTime(timezone=False), default=func.now(), nullable=False)
    data_atualizacao = Column('data_atualizacao', DateTime, onupdate=func.now())
    data_exclusao = Column('data_exclusao', DateTime(timezone=False), nullable=True, default=None)

    produto = relationship("ProdutoModel", back_populates="produto_estoque")
    tipo_estoque =  relationship("EstoqueTipoModel")


class EstoqueBaseModel(BaseModel):
    produto_id: int
    quantidade_disponivel: int
    data_cadastro: datetime
    data_atualizacao: Optional[datetime]

    tipo_estoque: Optional[EstoqueTipoBaseModel]


    @field_validator('data_cadastro', 'data_atualizacao')
    def format_datetime(cls, value):
        return format_datetime(value)

    class Config:
        from_attributes = True
