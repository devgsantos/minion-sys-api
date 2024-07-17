from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime,  Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from .base import Base
from pydantic import BaseModel, EmailStr, constr


class LoginModel(Base):
    __tablename__ = 'login'

    login_id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(200), nullable=False)
    senha = Column(String(200), nullable=False)
    codigo_confirmacao = Column(String(6))
    token = Column(String(1000))
    ultimo_login = Column('ultimo_login', DateTime(timezone=False), nullable=True)
    usuario_id = Column(Integer, ForeignKey('usuario.usuario_id'))

    usuario = relationship("UsuarioModel")
    permissoes = relationship("PermissaoModel")


class LoginBaseModel(BaseModel):
    login_id: int
    email: EmailStr
    senha: constr(max_length=200)
    codigo_confirmacao: Optional[constr(max_length=6)]
    token: Optional[constr(max_length=1000)]
    ultimo_login: Optional[datetime]
    usuario_id: Optional[int]

    class Config:
        orm_mode = True