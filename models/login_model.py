from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from .base import Base

class LoginModel(Base):
    __tablename__ = 'login'

    login_id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(200), nullable=False)
    senha = Column(String(200), nullable=False)
    codigo_confirmacao = Column(String(6))
    token = Column(String(1000))
    usuario_id = Column(Integer, ForeignKey('usuario.usuario_id'))

    usuario = relationship("usuario", back_populates="logins")
    permissoes = relationship("permissao", backref="login")
