from pydantic import BaseModel, constr, field_validator
from sqlalchemy import Column, func,  Integer, String, Numeric, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from models.base import Base
from datetime import datetime
from typing import List, Optional, Dict
from app.shared.helpers.validators import format_datetime
from .soft_delete import SoftDeleteQuery
from .datetime_fortaleza_local import fortaleza_now


class ProdutoTipoModel(Base, SoftDeleteQuery):
    __tablename__ = 'produto_tipo'
    produto_tipo_id = Column('produto_tipo_id', Integer, primary_key=True)
    titulo = Column('titulo', String(300), nullable=False)
    descricao = Column('descricao', String(500))
    imagem = Column('imagem', String(300))
    data_cadastro = Column('data_cadastro', DateTime(timezone=False), nullable=False, server_default=func.now(), default=func.now())
    data_atualizacao = Column('data_atualizacao', DateTime(timezone=False), onupdate=func.now())
    responsavel_cadastro_id = Column('responsavel_cadastro_id', Integer)
    empresa_id = Column('empresa_id', Integer)
    status = Column('status', Boolean, nullable=False, default=True)
    data_exclusao = Column('data_exclusao', DateTime)

class ProdutoTipoBaseModel(BaseModel):
    produto_tipo_id: int
    titulo: constr(max_length=300)
    descricao: Optional[constr(max_length=500)]
    imagem: Optional[str]
    data_cadastro: datetime
    data_atualizacao: Optional[datetime]
    responsavel_cadastro_id: int
    empresa_id: int
    status: bool
    data_exclusao: Optional[datetime]

    @field_validator('data_cadastro', 'data_atualizacao', 'data_exclusao')
    def format_datetime(cls, value):
        return format_datetime(value)

    class Config:
        from_attributes = True

class ProdutoTipoRequestModel(BaseModel):
    titulo: constr(max_length=300)
    descricao: Optional[constr(max_length=500)]
    imagem: Optional[Dict[str, str]] = None
    empresa_id: int

    @field_validator('imagem')
    def validate_imagem(cls, value):
        if value is None:
            return None
        
        # Verificar se é um dicionário válido
        if not isinstance(value, dict):
            raise ValueError('Campo imagem deve ser um objeto com as propriedades: tipo, arquivo')
        
        # Verificar se tem as chaves obrigatórias
        required_keys = {'tipo', 'arquivo'}
        if not all(key in value for key in required_keys):
            missing_keys = required_keys - set(value.keys())
            raise ValueError(f'Campos obrigatórios faltando em imagem: {missing_keys}')
        
        # Verificar se os valores são strings
        for key, val in value.items():
            if not isinstance(val, str):
                raise ValueError(f'Campo {key} em imagem deve ser string')
        
        # Verificar se arquivo não está vazio
        if not value['arquivo'].strip():
            raise ValueError('Campo arquivo em imagem não pode estar vazio')
        
        return value

    class Config:
        from_attributes = True
