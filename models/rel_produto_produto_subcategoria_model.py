from pydantic import BaseModel
from sqlalchemy import Column, func,  Integer, ForeignKey
from sqlalchemy.orm import relationship
from models.base import Base

class RelProdutoProdutoSubcategoria(Base):
    __tablename__ = 'rel_produto_produto_subcategoria'

    rel_produto_produto_subcategoria_id = Column(Integer, primary_key=True, autoincrement=True)
    produto_id = Column(Integer, ForeignKey('produto.produto_id'), nullable=False)
    produto_subcategoria_id = Column(Integer, ForeignKey('produto_subcategoria.produto_subcategoria_id'), nullable=False)

    sub_categorias = relationship('ProdutoSubcategoriaModel')

class RelProdutoProdutoSubcategoriaBaseModel(BaseModel):
    rel_produto_produto_subcategoria_id: int
    produto_id: int
    produto_subcategoria_id: int

    class Config:
        orm_mode = True