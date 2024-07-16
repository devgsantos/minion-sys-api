from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from pydantic import BaseModel
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
from datetime import datetime

from .base import Base
from models.soft_delete import SoftDeleteQuery
from .datetime_fortaleza_local import fortaleza_now


class EmpresaModel(Base, SoftDeleteQuery):
    __tablename__ = 'empresa'
    empresa_id = Column('empresa_id', Integer, primary_key=True)
    email = Column('email', String(200), nullable=False)
    nome = Column('nome', String(500), nullable=False)
    logradouro = Column('logradouro', String(300), nullable=False)
    numero_endereco = Column('numero_endereco', String(10), nullable=False)
    bairro = Column('bairro', String(100), nullable=False)
    cidade = Column('cidade', String(100), nullable=False)
    uf = Column('uf', String(2), nullable=False)
    telefone = Column('telefone', String, nullable=False)
    cpf = Column('cpf', String, nullable=True)
    cnpj = Column('cnpj', String, nullable=True)
    pais_id = Column('pais_id', Integer, ForeignKey('pais.pais_id'), nullable=False)
    naturalidade = Column('naturalidade', String(100), nullable=False)
    responsavel_cadastro = Column('responsavel_cadastro', String, nullable=True)
    empresa_categoria_id = Column('empresa_categoria_id', Integer, ForeignKey('empresa_categoria.empresa_categoria_id'),
                                  nullable=False)
    data_cadastro = Column('data_cadastro', DateTime, default=fortaleza_now, nullable=False)
    data_atualizacao = Column('data_atualizacao', DateTime, nullable=True)
    status = Column('status', Boolean, nullable=False)
    data_exclusao = Column('data_exclusao', DateTime, nullable=True, default=None)

    empresa_categoria = relationship('EmpresaCategoria', back_populates='empresas')
    pais = relationship('pais', back_populates='empresas')

class EmpresaBase(BaseModel):
    EmpresaId: int
    Email: str
    Nome: str
    Logradouro: str
    NumeroEndereco: str
    Bairro: str
    Cidade: str
    UF: str
    Telefone: str
    Cpf: str = None
    Cnpj: str = None
    Nacionalidade: str
    Naturalidade: str
    ResponsavelCadastro: str = None
    Status: bool
