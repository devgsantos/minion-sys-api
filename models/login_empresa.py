from sqlalchemy import Column, func, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from models.base import Base
from pydantic import BaseModel


class LoginEmpresaModel(Base):
    __tablename__ = 'login_empresa'

    login_empresa_id = Column(Integer, primary_key=True, autoincrement=True)
    login_id = Column(Integer, ForeignKey('login.login_id'), nullable=False)
    empresa_id = Column(Integer, ForeignKey('empresa.empresa_id'), nullable=False)
    data_cadastro = Column('data_cadastro', DateTime(timezone=False), default=func.now(), nullable=False)
    data_exclusao = Column('data_exclusao', DateTime)

    login = relationship('LoginModel')
    empresa = relationship('EmpresaModel')


class LoginEmpresaBaseModel(BaseModel):
    login_empresa_id: int
    login_id: int
    empresa_id: int

    class Config:
        from_attributes = True