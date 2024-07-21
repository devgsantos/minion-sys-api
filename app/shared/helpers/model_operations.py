import os
from typing import Type, List, Optional, Any

from flask import request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, joinedload
from sqlalchemy.orm.exc import NoResultFound
from contextlib import contextmanager

from app.shared.singletons.logger import Logger
from models.base import Base


# Classe que abstrai operações com modelos SQLAlchemy
class ModelOperations:
    def __init__(self):
        self.Session = request.db_session
        self.logger = Logger()


    # Context manager para gerenciar a sessão do SQLAlchemy
    @contextmanager
    def session_scope(self):
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception as exc:
            self.logger.log(message=str(f"ModelOperations -> {exc}"), level='error')
            session.rollback()
            raise
        # finally:
        #     session.close()

    # Buscar todos os registros de um modelo
    def findAll(self, model: Type[Base]) -> List[Any]:
        with self.session_scope() as session:
            return session.query(model).options(joinedload('*')).all()

    # Buscar um único registro baseado em uma condição
    def findOne(self,  model: Type[Base], **kwargs) -> Optional[Any]:
        with self.session_scope() as session:
            try:
                results = session.query(model).filter_by(**kwargs).one()
                return results
            except NoResultFound:
                return None

    # Buscar um registro pelo ID
    def findById(self, model: Type[Base], id: int) -> Optional[Any]:
        with self.session_scope() as session:
            return session.query(model).get(id)

    # Inserir um novo registro
    def insert(self, model: Type[Base], data: dict) -> Any:
        with self.session_scope() as session:
            instance = model(**data)
            session.add(instance)
            return instance

    # Atualizar um registro existente
    def update(self, model: Type[Base], instance_id: int, **kwargs) -> Optional[Any]:
        instance = self.Session.query(model).get(instance_id)
        if instance:
            for key, value in kwargs.items():
                setattr(instance, key, value)
            self.Session.commit()
            return instance
        return None

    # Deletar um registro
    def delete(self, model: Type[Base], id: int) -> bool:
        with self.session_scope() as session:
            instance = session.query(model).get(id)
            if instance:
                session.delete(instance)
                return True
            return False

    def model_to_dict(self, model_instance):
        return {c.name: getattr(model_instance, c.name) for c in model_instance.__table__.columns}

