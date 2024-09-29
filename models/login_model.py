from datetime import datetime
from typing import Optional, List, Any

from sqlalchemy import Column, DateTime, Integer, String, ForeignKey, func
from sqlalchemy.orm import relationship

from models.base import Base
from pydantic import BaseModel, EmailStr, constr


class LoginModel(Base):
    __tablename__ = 'login'

    login_id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(200), nullable=False)
    senha = Column(String(200), nullable=False)
    codigo_confirmacao = Column(String(6))
    token = Column(String(1000))
    ultimo_login = Column('ultimo_login', DateTime(timezone=False), nullable=True)
    data_cadastro = Column('data_cadastro', DateTime(timezone=False), default=func.now(), nullable=False)
    data_exclusao = Column('data_exclusao', DateTime)

    usuario = relationship("UsuarioModel")
    permissoes = relationship("LoginPermissaoModel")
    empresas = relationship("LoginEmpresaModel")


class LoginBaseModel(BaseModel):
    login_id: int
    email: EmailStr
    senha: constr(max_length=200)
    codigo_confirmacao: Optional[constr(max_length=6)]
    token: Optional[constr(max_length=1000)]
    ultimo_login: Optional[datetime]
    data_atualizacao: Optional[datetime]
    usuario_id: Optional[int]
    permissoes: Optional[List[Any]]
    permissoes_id: Optional[List[Any]]

    class Config:
        from_attributes = True


class LoginRequestModel(BaseModel):
    email: str
    senha: constr(max_length=200)


class LoginPermissoesRequest(BaseModel):
    login_id: int
    permissoes_id: List[int]
