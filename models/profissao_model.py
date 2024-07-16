from sqlalchemy import Column, Integer, String, DateTime
from pydantic import BaseModel
from typing import Optional

from .base import Base
from .soft_delete import SoftDeleteQuery


class ProfissaoModel(Base, SoftDeleteQuery):
    __tablename__ = 'profissao'

    profissao_id = Column('profissao_id', Integer, primary_key=True)
    titulo = Column('titulo', String(300), nullable=False)
    descricao = Column('descricao', String(500))
    imagem = Column('imagem', String(300))
    data_exclusao = Column('data_exclusao', DateTime)

class ProfissaoSchema(BaseModel):
    Titulo: str
    Descricao: Optional[str] = None
    Imagem: Optional[str] = None

class ProfissaoCreate(ProfissaoSchema):
    pass

class Profissao(ProfissaoSchema):
    ProfissaoId: int
