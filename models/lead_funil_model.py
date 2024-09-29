from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, constr
from sqlalchemy import Column, func,  Integer, ForeignKey, Boolean, String, DateTime
from sqlalchemy.orm import relationship

from models.base import Base
from models.soft_delete import SoftDeleteQuery


class LeadFunilModel(Base, SoftDeleteQuery):
    __tablename__ = 'lead_funil'

    funil_id = Column('funil_id', Integer, primary_key=True)
    titulo = Column('titulo', String(300), nullable=False)
    descricao = Column('descricao', String(500))
    imagem = Column('imagem', String(300))
    data_cadastro = Column('data_cadastro', DateTime(timezone=False), nullable=False, server_default=func.now(),
                           default=func.now())
    data_exclusao = Column('data_exclusao', DateTime)


class LeadFunilBaseModel(BaseModel):
    funil_id: int
    titulo: constr(max_length=300)
    descricao: Optional[constr(max_length=500)] = None
    imagem: Optional[constr(max_length=300)] = None
    data_cadastro: datetime
    data_exclusao: Optional[datetime] = None

    class Config:
        from_attibutes = True