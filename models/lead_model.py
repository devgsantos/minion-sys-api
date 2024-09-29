from datetime import datetime

from pydantic import BaseModel, EmailStr, constr
from sqlalchemy import Column, func,  Integer, ForeignKey, Boolean, String, DateTime
from sqlalchemy.orm import relationship

from models.base import Base
from models.soft_delete import SoftDeleteQuery
from .datetime_fortaleza_local import fortaleza_now
from typing import Optional


class LeadModel(Base, SoftDeleteQuery):
    __tablename__ = 'lead'

    lead_id = Column('lead_id', Integer, primary_key=True)
    email = Column('email', String(200), nullable=False)
    nome_completo = Column('nome_completo', String(500), nullable=False)
    logradouro = Column('logradouro', String(300), nullable=False)
    numero_endereco = Column('numero_endereco', String(10), nullable=False)
    bairro = Column('bairro', String(100), nullable=False)
    cidade = Column('cidade', String(100), nullable=False)
    uf = Column('uf', String(2), nullable=False)
    profissao_id = Column('profissao_id', Integer, ForeignKey('profissao.profissao_id'), nullable=False)
    telefone = Column('telefone', String, nullable=False)
    cpf = Column('cpf', String)
    cnpj = Column('cnpj', String)
    pais_id = Column('nacionalidade', Integer, ForeignKey('pais.pais_id'), nullable=False)
    naturalidade = Column('naturalidade', String(100), nullable=False)
    responsavel_cadastro = Column('responsavel_cadastro', String)
    data_cadastro = Column('data_cadastro', DateTime(timezone=False), default=func.now(), nullable=False)
    data_atualizacao = Column('data_atualizacao', DateTime(timezone=False), onupdate=func.now())
    status = Column('status', Boolean, nullable=False, default=True)
    data_exclusao = Column('data_exclusao', DateTime(timezone=False), nullable=True, default=None)

    profissao = relationship('ProfissaoModel')
    pais = relationship('PaisModel')

class LeadBaseModel(BaseModel):
    lead_id: int
    email: EmailStr
    nome_completo: constr(max_length=500)
    logradouro: constr(max_length=300)
    numero_endereco: constr(max_length=10)
    bairro: constr(max_length=100)
    cidade: constr(max_length=100)
    uf: constr(max_length=2)
    profissao_id: int
    telefone: str
    cpf: Optional[str]
    cnpj: Optional[str]
    nacionalidade: constr(max_length=100)
    naturalidade: constr(max_length=100)
    responsavel_cadastro: Optional[str]
    data_cadastro: datetime
    data_atualizacao: Optional[datetime]
    status: bool
    data_exclusao: Optional[datetime]

    class Config:
        from_attributes = True