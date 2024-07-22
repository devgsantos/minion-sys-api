from pydantic import BaseModel, constr
from sqlalchemy import Column, func,  Integer, String, Numeric, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from models.base import Base
from datetime import datetime
from typing import List, Optional

from .soft_delete import SoftDeleteQuery
from .datetime_fortaleza_local import fortaleza_now


class ProdutoTipoModel(Base, SoftDeleteQuery):
    __tablename__ = 'produto_tipo'
    produto_tipo_id = Column('produto_tipo_id', Integer, primary_key=True)
    titulo = Column('titulo', String(300), nullable=False)
    descricao = Column('descricao', String(500))
    imagem = Column('imagem', String(300))
    data_cadastro = Column('data_cadastro', DateTime(timezone=False), nullable=False, server_default=func.now(), default=func.now())
    data_atualizacao = Column('data_atualizacao', DateTime, onupdate=func.now())
    responsavel_cadastro = Column('responsavel_cadastro', String(100), nullable=False)
    status = Column('status', Boolean, nullable=False, default=True)
    delet = Column('delet', Boolean, nullable=False)
    data_exclusao = Column('data_exclusao', DateTime)

    produtos = relationship('ProdutoModel', back_populates='produto_tipo')
class ProdutoTipoBaseModel(BaseModel):
    produto_tipo_id: int
    titulo: constr(max_length=300)
    descricao: Optional[constr(max_length=500)]
    imagem: Optional[str]
    data_cadastro: datetime
    data_atualizacao: Optional[datetime]
    responsavel_cadastro: constr(max_length=100)
    status: bool
    delet: bool
    data_exclusao: Optional[datetime]

    class Config:
        orm_mode = True