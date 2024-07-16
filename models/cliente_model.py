from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import sessionmaker, scoped_session, relationship
from datetime import datetime

from .base import Base
from pydantic import BaseModel
from typing import Optional

from models.soft_delete import SoftDeleteQuery
from .datetime_fortaleza_local import fortaleza_now


class ClienteModel(Base, SoftDeleteQuery):
    __tablename__ = 'cliente'
    query = scoped_session(sessionmaker(query_cls=SoftDeleteQuery))
    cliente_id = Column('cliente_id', Integer, primary_key=True)
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
    pais_id = Column('pais_id', Integer, nullable=False)
    naturalidade = Column('naturalidade', String(100), nullable=False)
    responsavel_cadastro = Column('responsavel_cadastro', String, nullable=True)
    data_cadastro = Column('data_cadastro', DateTime, default=fortaleza_now, nullable=False)
    data_atualizacao = Column('data_atualizacao', DateTime, nullable=True)
    status = Column('status', Integer, nullable=False)
    data_exclusao = Column('data_exclusao', DateTime, nullable=True, default=None)

    pais = relationship('pais', back_populates='clientes')

class ClienteBase(BaseModel):
    ClienteId: int
    Email: str
    Nome: str
    Logradouro: str
    NumeroEndereco: str
    Bairro: str
    Cidade: str
    UF: str
    Telefone: str
    Cpf: Optional[str] = None
    Cnpj: Optional[str] = None
    Nacionalidade: str
    Naturalidade: str
    ResponsavelCadastro: Optional[str] = None
    Status: bool
