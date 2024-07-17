from sqlalchemy import Column, func,  Integer, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base
from pydantic import BaseModel


class LoginEmpresaModel(Base):
    __tablename__ = 'login_empresa'

    login_empresa_id = Column(Integer, primary_key=True, autoincrement=True)
    login_id = Column(Integer, ForeignKey('login.login_id'), nullable=False)
    empresa_id = Column(Integer, ForeignKey('empresa.empresa_id'), nullable=False)

    login = relationship('login', backref='login_empresas')
    empresa = relationship('empresa', backref='login_empresas')


class LoginEmpresaBaseModel(BaseModel):
    login_empresa_id: int
    login_id: int
    empresa_id: int

    class Config:
        orm_mode = True