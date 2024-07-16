from datetime import datetime

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from pydantic import BaseModel

from .base import Base
from .datetime_fortaleza_local import fortaleza_now


class UsuarioModel(Base):
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
    telefone = Column('telefone', String, nullable=False)
    cpf = Column('cpf', String(14), nullable=False)
    pais_id = Column('nacionalidade', Integer, ForeignKey('pais.pais_id'), nullable=False)
    naturalidade = Column('naturalidade', String(150), nullable=False)
    foto = Column('foto', String(300))
    data_cadastro = Column('data_cadastro', DateTime, nullable=False, default=fortaleza_now)
    data_atualizacao = Column('data_atualizacao', DateTime)
    status = Column('status', Boolean, nullable=False)
    data_exclusao = Column('data_exclusao', DateTime)

    profissao = relationship('ProfissaoModel', back_populates='usuarios')
    pais = relationship('PaisModel', back_populates='usuarios')


class UsuarioSchema(BaseModel):
    Email: str
    Nome: str
    Logradouro: str
    NumeroEndereco: str
    Bairro: str
    Cidade: str
    UF: str
    ProfissaoId: int
    Telefone: str
    Cpf: str
    Nacionalidade: str
    Naturalidade: str
    Status: bool
    Delet: bool

class UsuarioCreate(UsuarioSchema):
    pass

class Usuario(UsuarioSchema):
    UsuarioId: int
