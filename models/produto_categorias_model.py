from datetime import datetime
from typing import Optional, Dict

from pydantic import BaseModel, constr, field_validator
from sqlalchemy import Column, func,  Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from models.base import Base
from .soft_delete import SoftDeleteQuery
from app.shared.helpers.validators import format_datetime
from .datetime_fortaleza_local import fortaleza_now


class ProdutoCategoriaModel(Base, SoftDeleteQuery):
    __tablename__ = 'produto_categoria'
    produto_categoria_id = Column('produto_categoria_id', Integer, primary_key=True)
    titulo = Column('titulo', String(300), nullable=False)
    descricao = Column('descricao', String(500))
    sigla = Column('sigla', String(3), nullable=False)
    imagem = Column('imagem', String(300))
    data_cadastro = Column('data_cadastro', DateTime(timezone=False), default=func.now())
    data_atualizacao = Column('data_atualizacao', DateTime(timezone=False), onupdate=func.now())
    responsavel_cadastro_id = Column('responsavel_cadastro_id', Integer)
    empresa_id = Column('empresa_id', Integer)
    status = Column('status', Boolean, default=True)
    data_exclusao = Column('data_exclusao', DateTime)

    # produtos = relationship('ProdutoModel', back_populates='produto_categoria')


class ProdutoCategoriaBaseModel(BaseModel):
    produto_categoria_id: int
    titulo: Optional[constr(max_length=300)]
    descricao: Optional[constr(max_length=500)]
    sigla: Optional[constr(max_length=3)]
    imagem: Optional[str]
    data_cadastro: Optional[datetime]
    data_atualizacao: Optional[datetime]
    responsavel_cadastro_id: int
    empresa_id: int
    status: Optional[bool]
    data_exclusao: Optional[datetime]

    @field_validator('data_cadastro', 'data_atualizacao', 'data_exclusao')
    def format_datetime(cls, value):
        return format_datetime(value)

    class Config:
        from_attributes = True


class ProdutoCategoriaRequestModel(BaseModel):
    titulo: constr(max_length=300)
    descricao: Optional[constr(max_length=500)]
    imagem: Optional[Dict[str, str]] = None
    sigla: str
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

