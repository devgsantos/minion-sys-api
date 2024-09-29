from datetime import datetime
from typing import Optional

from sqlalchemy import func,  Column, Integer, String, Boolean, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from pydantic import BaseModel, constr, EmailStr

from models.base import Base
from .datetime_fortaleza_local import fortaleza_now
from .soft_delete import SoftDeleteQuery


class UsuarioModel(Base, SoftDeleteQuery):
    __tablename__ = 'usuario'

    usuario_id = Column('usuario_id', Integer, primary_key=True, nullable=False)
    email = Column('email', String(200), nullable=False)
    nome = Column('nome', String(500), nullable=False)
    logradouro = Column('logradouro', String(300), nullable=False)
    numero_endereco = Column('numero_endereco', String(10), nullable=False)
    bairro = Column('bairro', String(100), nullable=False)
    cidade = Column('cidade', String(100), nullable=False)
    uf = Column('uf', String(2), nullable=False)
    profissao_id = Column('profissao_id', Integer, ForeignKey('profissao.profissao_id'), nullable=False)
    login_id = Column('login_id', Integer, ForeignKey('login.login_id'), unique=True, nullable=False)
    telefone = Column('telefone', String, nullable=False)
    cpf = Column('cpf', String(14), unique=True, nullable=False)
    pais_id = Column('nacionalidade', Integer, ForeignKey('pais.pais_id'), nullable=False)
    naturalidade = Column('naturalidade', String(150), nullable=False)
    foto = Column('foto', String(300), nullable=True)
    data_cadastro = Column('data_cadastro', DateTime(timezone=False), nullable=False, server_default=func.now(), default=func.now())
    data_atualizacao = Column('data_atualizacao', DateTime(timezone=False), onupdate=func.now())
    status = Column('status', Boolean, nullable=False, default=True)
    data_exclusao = Column('data_exclusao', DateTime)

    profissao = relationship('ProfissaoModel')
    pais = relationship('PaisModel')



class UsuarioBaseModel(BaseModel):
    usuario_id: int
    email: constr(max_length=200)
    nome: constr(max_length=500)
    logradouro: constr(max_length=300)
    numero_endereco: constr(max_length=10)
    bairro: constr(max_length=100)
    cidade: constr(max_length=100)
    uf: constr(max_length=2)
    profissao_id: int
    telefone: str
    cpf: constr(max_length=14)
    pais_id: int
    naturalidade: constr(max_length=150)
    foto: Optional[str]
    data_cadastro: datetime
    data_atualizacao: Optional[datetime]
    status: bool
    data_exclusao: Optional[datetime]

    class Config:
        from_attributes = True

class UsuarioRequestModel(BaseModel):
    email: EmailStr
    nome: str
    logradouro: str
    numero_endereco: str
    bairro: str
    cidade: str
    uf: str
    profissao_id: int
    telefone: str
    cpf: str
    pais_id: int
    naturalidade: str
    foto: Optional[str]
