from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from .base import Base
from datetime import datetime
from typing import List, Optional

from .produto_model import ProdutoSchema
from .soft_delete import SoftDeleteQuery
from .datetime_fortaleza_local import fortaleza_now


class ProdutoTipoModel(Base, SoftDeleteQuery):
    __tablename__ = 'produto_tipo'
    produto_tipo_id = Column('produto_tipo_id', Integer, primary_key=True)
    titulo = Column('titulo', String(300), nullable=False)
    descricao = Column('descricao', String(500))
    imagem = Column('imagem', String(300))
    data_cadastro = Column('data_cadastro', DateTime, nullable=False, default=fortaleza_now)
    data_atualizacao = Column('data_atualizacao', DateTime)
    responsavel_cadastro = Column('responsavel_cadastro', String(100), nullable=False)
    status = Column('status', Boolean, nullable=False)
    delet = Column('delet', Boolean, nullable=False)
    data_exclusao = Column('data_exclusao', DateTime)

    produtos = relationship('produto', backref='produto_tipo')
class ProdutoTipoSchema(BaseModel):
    ProdutoTipoId: int
    Titulo: str
    Descricao: Optional[str] = None
    Imagem: Optional[str] = None
    DataCadastro: datetime
    ResponsavelCadastro: str
    Status: bool
    produtos: List[ProdutoSchema] = []