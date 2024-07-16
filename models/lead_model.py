from datetime import datetime

from pydantic import BaseModel
from sqlalchemy import Column, Integer, ForeignKey, Boolean, String, DateTime
from sqlalchemy.orm import relationship

from .base import Base
from .soft_delete import SoftDeleteQuery
from .datetime_fortaleza_local import fortaleza_now


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
    nacionalidade = Column('nacionalidade', String(100), nullable=False)
    naturalidade = Column('naturalidade', String(100), nullable=False)
    responsavel_cadastro = Column('responsavel_cadastro', String)
    data_cadastro = Column('data_cadastro', DateTime, default=fortaleza_now, nullable=False)
    data_atualizacao = Column('data_atualizacao', DateTime, nullable=True)
    status = Column('status', Boolean, nullable=False)
    delet = Column('delet', Boolean, nullable=False)
    data_exclusao = Column('data_exclusao', DateTime, nullable=True, default=None)

    profissao = relationship('profissao')

class LeadSchema(BaseModel):
    Email: str
    NomeCompleto: str
    Logradouro: str
    NumeroEndereco: str
    Bairro: str
    Cidade: str
    UF: str
    ProfissaoId: int
    Telefone: str
    Cpf: str = None
    Cnpj: str = None
    Nacionalidade: str
    Naturalidade: str
    ResponsavelCadastro: str = None
    Status: bool

class LeadCreate(LeadSchema):
    pass

class Lead(LeadSchema):
    LeadId: int
