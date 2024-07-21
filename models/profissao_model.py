from datetime import datetime

from sqlalchemy import Column, func,  Integer, String, DateTime
from pydantic import BaseModel, constr
from typing import Optional

from models.base import Base
from .soft_delete import SoftDeleteQuery


class ProfissaoModel(Base, SoftDeleteQuery):
    __tablename__ = 'profissao'

    profissao_id = Column('profissao_id', Integer, primary_key=True)
    titulo = Column('titulo', String(300), nullable=False)
    descricao = Column('descricao', String(500))
    imagem = Column('imagem', String(300))
    data_exclusao = Column('data_exclusao', DateTime)

class ProfissaoBaseModel(BaseModel):
    profissao_id: int
    titulo: constr(max_length=300)
    descricao: Optional[constr(max_length=500)]
    imagem: Optional[str]
    data_exclusao: Optional[datetime]

    class Config:
        orm_mode = True