from sqlalchemy import Column, func,  Integer, String, ForeignKey, DateTime
from pydantic import BaseModel, constr
from models.base import Base
from .soft_delete import SoftDeleteQuery

class OrcamentoStatusModel(Base, SoftDeleteQuery):
    __tablename__ = 'orcamento_status'

    orcamento_status_id = Column('orcamento_status_id', Integer, primary_key=True)
    titulo = Column('titulo', String(500))
    descricao = Column('descricao', String(1000), nullable=True)
    empresa_id = Column('empresa_id', Integer, ForeignKey('empresa.empresa_id'), nullable=False)
    data_cadastro = Column('data_cadastro', DateTime(timezone=False), default=func.now(), nullable=False)
    data_atualizacao = Column('data_atualizacao', DateTime(timezone=False), onupdate=func.now())
    data_exclusao = Column('data_exclusao', DateTime(timezone=False), nullable=True)


class OrcamentoStatusBaseModel(BaseModel):
    orcamento_status_id: int
    titulo: constr(max_length=500)
    descricao: constr(max_length=1000)

    class Config:
        from_attributes = True