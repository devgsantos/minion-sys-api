from sqlalchemy import Column, func,  Integer, String, ForeignKey, DateTime
from pydantic import BaseModel
from typing import Optional

from datetime import datetime

from models.base import Base
from .soft_delete import SoftDeleteQuery
from .datetime_fortaleza_local import fortaleza_now

# TODO -> Criar modelo de status de orcamento e relações

class OrcamentoStatusModel(Base, SoftDeleteQuery):
    __tablename__ = 'orcamento_status'

    orcamento_status_id = Column('orcamento_status_id', Integer, primary_key=True)
    titulo = Column('titulo', String(500))
    descricao = Column('descricao', String(1000), nullable=True)
    empresa_id = Column('empresa_id', Integer, ForeignKey('empresa.empresa_id'), nullable=True)
    data_cadastro = Column('data_cadastro', DateTime(timezone=False), default=func.now(), nullable=False)
    data_atualizacao = Column('data_atualizacao', DateTime(timezone=False), onupdate=func.now())
    data_exclusao = Column('data_exclusao', DateTime(timezone=False), nullable=True, default=None)


class OrcamentoStatusBaseModel(BaseModel):
    orcamento_id: int
    cliente_id: Optional[int]
    data_cadastro: datetime
    data_atualizacao: Optional[datetime]
    finalizado: bool
    delet: bool
    data_exclusao: Optional[datetime]

    class Config:
        from_attributes = True