from pydantic import BaseModel
from sqlalchemy import Column, func,  Integer, ForeignKey
from sqlalchemy.orm import relationship
from models.base import Base

class RelServicoProdutoModel(Base):
    __tablename__ = 'rel_servico_produto'

    rel_servico_produto_id = Column(Integer, primary_key=True, autoincrement=True)
    servico_id = Column(Integer, nullable=False)
    produto_id = Column(Integer, nullable=False)


class RelProdutoProdutoSubcategoriaBaseModel(BaseModel):
    rel_servico_produto_id: int
    servico_id: int
    produto_id: int

    class Config:
        from_attributes = True