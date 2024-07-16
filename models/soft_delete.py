from sqlalchemy import Column, DateTime
from sqlalchemy.orm import Query
from sqlalchemy.ext.declarative import declared_attr
from datetime import datetime

class SoftDeleteQuery(Query):
    def __new__(cls, *args, **kwargs):
        obj = super(SoftDeleteQuery, cls).__new__(cls)
        obj.__hidden_filters__ = []
        return obj

    def __init__(self, *args, **kwargs):
        super(SoftDeleteQuery, self).__init__(*args, **kwargs)
        self.__hidden_filters__.append(self._soft_deleted_filter)

    def _soft_deleted_filter(self, query):
        return query.filter_by(deleted_at=None)

    def soft_delete(self):
        self.update({"deleted_at": datetime.utcnow()})

class SoftDeleteMixin:
    @declared_attr
    def data_exclusao(cls):
        return Column(DateTime, nullable=True)

    def delete(self):
        self.data_exclusao = datetime.utcnow()

    def restore(self):
        self.data_exclusao = None

