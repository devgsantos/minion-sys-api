from pydantic import BaseModel
from sqlalchemy import Column, func,  Integer, ForeignKey
from sqlalchemy.orm import relationship
from models.base import Base

class LoginPermissaoModel(Base):
    __tablename__ = 'login_permissao'

    login_permissao_id = Column(Integer, primary_key=True, autoincrement=True)
    login_id = Column(Integer, ForeignKey('login.login_id'), nullable=False)
    permissao_id = Column(Integer, ForeignKey('permissao.permissao_id'), nullable=False)

    login = relationship('LoginModel')
    permissao = relationship('PermissaoModel')

class LoginPermissaoBaseModel(BaseModel):
    login_permissao_id: int
    login_id: int
    permissao_id: int

    class Config:
        orm_mode = True