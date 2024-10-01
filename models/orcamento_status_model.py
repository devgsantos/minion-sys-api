from tokenize import String

from sqlalchemy import Column, func,  Integer, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from typing import Optional

from datetime import datetime

from models.base import Base
from .soft_delete import SoftDeleteQuery
from .datetime_fortaleza_local import fortaleza_now

# TODO -> Criar modelo de status de orcamento

class OrcamentoModel(Base, SoftDeleteQuery):
    __tablename__ = 'orcamento_status'

    orcamento_status_id = Column('orcamento_status_id', Integer, primary_key=True)
    titulo = Column('titulo', Integer, ForeignKey('cliente.cliente_id'))
    descricao = Column('descricao', String(1000), nullable=True)
    data_cadastro = Column('data_cadastro', DateTime(timezone=False), default=func.now(), nullable=False)
    data_atualizacao = Column('data_atualizacao', DateTime(timezone=False), onupdate=func.now())
    orcamento_status_id = Column('orcamento_status_id', Integer, nullable=False, default=1)
    data_exclusao = Column('data_exclusao', DateTime(timezone=False), nullable=True, default=None)


class OrcamentoBaseModel(BaseModel):
    orcamento_id: int
    cliente_id: Optional[int]
    data_cadastro: datetime
    data_atualizacao: Optional[datetime]
    finalizado: bool
    delet: bool
    data_exclusao: Optional[datetime]

    class Config:
        from_attributes = True