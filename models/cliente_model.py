from sqlalchemy import func, Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, scoped_session, relationship
from datetime import datetime

from models.base import Base
from pydantic import BaseModel, EmailStr, constr
from typing import Optional

from models.soft_delete import SoftDeleteQuery
from .datetime_fortaleza_local import fortaleza_now
from .pais_model import PaisBaseModel


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
    pais_id = Column('nacionalidade', Integer, ForeignKey('pais.pais_id'), nullable=False)
    naturalidade = Column('naturalidade', String(100), nullable=False)
    responsavel_cadastro = Column('responsavel_cadastro', String, nullable=True)
    data_cadastro = Column('data_cadastro', DateTime(timezone=False), default=func.now(), nullable=False)
    data_atualizacao = Column('data_atualizacao', DateTime(timezone=False), onupdate=func.now())
    data_exclusao = Column('data_exclusao', DateTime(timezone=False), nullable=True, default=None)
    lead_id = Column(Integer, nullable=True)

    pais = relationship('PaisModel')

class ClienteBaseModel(BaseModel):
    cliente_id: int
    email: EmailStr
    nome: constr(max_length=500)
    logradouro: constr(max_length=300)
    numero_endereco: constr(max_length=10)
    bairro: constr(max_length=100)
    cidade: constr(max_length=100)
    uf: constr(max_length=2)
    telefone: str
    cpf: Optional[str]
    cnpj: Optional[str]
    pais_id: Optional[PaisBaseModel]
    naturalidade: constr(max_length=100)
    responsavel_cadastro: Optional[str]
    data_cadastro: datetime
    data_atualizacao: Optional[datetime]
    status: int
    lead_conversao: Optional[int]
    data_exclusao: Optional[datetime]

    class Config:
        from_attributes = True

class ClienteServicoBaseModel(BaseModel):
    cliente_id: int
    email: EmailStr
    nome: constr(max_length=500)
    cpf: Optional[str]
    cnpj: Optional[str]

    class Config:
        from_attributes = True