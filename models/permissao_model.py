from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from .base import Base

class PermissaoModel(Base):
    __tablename__ = 'permissao'

    permissao_id = Column(Integer, primary_key=True, autoincrement=True)
    titulo = Column(String(255), nullable=False)
    apelido = Column(String(100), nullable=False)
    descricao = Column(String(500))
