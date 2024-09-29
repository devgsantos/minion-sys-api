from typing import Optional

from pydantic import constr, BaseModel
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from models.base import Base

class PermissaoModel(Base):
    __tablename__ = 'permissao'

    permissao_id = Column(Integer, primary_key=True, autoincrement=True)
    titulo = Column(String(255), nullable=False)
    apelido = Column(String(100), nullable=False)
    descricao = Column(String(500))
    data_exclusao = Column('data_exclusao', DateTime)

class PermissaoBaseModel(BaseModel):
    permissao_id: int
    titulo: constr(max_length=255)
    apelido: constr(max_length=100)
    descricao: Optional[constr(max_length=500)]

    class Config:
        from_attibutes = True