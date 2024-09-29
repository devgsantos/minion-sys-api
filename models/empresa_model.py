from datetime import datetime
from typing import Optional

from sqlalchemy import Column, func,  Integer, String, Boolean, DateTime, ForeignKey
from pydantic import BaseModel, EmailStr, constr
from sqlalchemy.orm import relationship

from models.base import Base
from models.soft_delete import SoftDeleteQuery

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
    cpf = Column('cpf', String, unique=True, nullable=True)
    cnpj = Column('cnpj', String, unique=True, nullable=True)
    pais_id = Column('pais_id', Integer, ForeignKey('pais.pais_id'), nullable=False)
    responsavel_cadastro_id = Column('responsavel_cadastro_id', Integer, ForeignKey('login.login_id'),
                                  nullable=False)
    empresa_categoria_id = Column('empresa_categoria_id', Integer, ForeignKey('empresa_categoria.empresa_categoria_id'),
                                  nullable=False)
    data_cadastro = Column('data_cadastro', DateTime(timezone=False), default=func.now(), nullable=False)
    data_atualizacao = Column('data_atualizacao', DateTime(timezone=False), onupdate=func.now())
    status = Column('status', Boolean, nullable=False, default=True)
    data_exclusao = Column('data_exclusao', DateTime(timezone=False), nullable=True, default=None)

    empresa_categoria = relationship('EmpresaCategoriaModel')
    pais = relationship('PaisModel')


class EmpresaBaseModel(BaseModel):
    empresa_id: int
    email: EmailStr
    nome: constr(max_length=500)
    filial: int
    logradouro: constr(max_length=300)
    numero_endereco: constr(max_length=10)
    bairro: constr(max_length=100)
    cidade: constr(max_length=100)
    uf: constr(max_length=2)
    telefone: str
    cpf: Optional[str]
    cnpj: Optional[str]
    pais_id: int
    naturalidade: constr(max_length=100)
    responsavel_cadastro: Optional[str]
    empresa_categoria_id: int
    data_cadastro: datetime
    data_atualizacao: Optional[datetime]
    status: bool
    data_exclusao: Optional[datetime]

    class Config:
        from_attributes = True


class EmpresaRequestModel(BaseModel):
    email: EmailStr
    nome: constr(max_length=500)
    logradouro: constr(max_length=300)
    numero_endereco: constr(max_length=10)
    bairro: constr(max_length=100)
    cidade: constr(max_length=100)
    uf: constr(max_length=2)
    filial: int
    telefone: str
    cpf: Optional[str]
    cnpj: Optional[str]
    pais_id: int
    empresa_categoria_id: int
