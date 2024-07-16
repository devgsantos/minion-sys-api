from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class LoginPermissaoModel(Base):
    __tablename__ = 'login_permissao'

    login_permissao_id = Column(Integer, primary_key=True, autoincrement=True)
    login_id = Column(Integer, ForeignKey('login.login_id'), nullable=False)
    permissao_id = Column(Integer, ForeignKey('permissao.permissao_id'), nullable=False)

    login = relationship('login', backref='login_permissoes')
    permissao = relationship('permissao', backref='login_permissoes')