from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

from .base import Base
from .soft_delete import SoftDeleteQuery
from .datetime_fortaleza_local import fortaleza_now


class EmpresaCategoriaModel(Base, SoftDeleteQuery):
    __tablename__ = 'empresa_categoria'

    empresa_categoria_id = Column('empresa_categoria_id', Integer, primary_key=True)
    titulo = Column('titulo', String(300), nullable=False)
    descricao = Column('descricao', String(500), nullable=True)
    sigla = Column('sigla', String(3), nullable=False)
    imagem = Column('imagem', String(300), nullable=True)
    data_cadastro = Column('data_cadastro', DateTime, default=fortaleza_now, nullable=True)
    data_atualizacao = Column('data_atualizacao', DateTime, nullable=True)
    data_exclusao = Column('data_exclusao', DateTime, nullable=True, default=None)


    def __init__(self, titulo, sigla, descricao=None, imagem=None, data_cadastro=None, data_atualizacao=None):
        self.titulo = titulo
        self.descricao = descricao
        self.sigla = sigla
        self.imagem = imagem
        self.data_cadastro = data_cadastro or datetime.utcnow()
        self.data_atualizacao = data_atualizacao
