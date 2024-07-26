from sqlalchemy import Column, func,  DateTime
from sqlalchemy.orm import Query
from sqlalchemy.ext.declarative import declared_attr
from datetime import datetime

from models.datetime_fortaleza_local import fortaleza_now


class SoftDeleteQuery:
    def __new__(cls, *args, **kwargs):
        obj = super(SoftDeleteQuery, cls).__new__(cls)
        obj.__hidden_filters__ = []
        return obj

    def __init__(self, *args, **kwargs):
        super(SoftDeleteQuery, self).__init__(*args, **kwargs)
        self.__hidden_filters__.append(self._soft_deleted_filter)

    def _soft_deleted_filter(self, query):
        return query.filter_by(data_exclusao=None)

    def soft_delete(self):
        self.update({"data_exclusao": datetime.utcnow()})

class SoftDeleteMixin:
    def __init__(self):
        self.data_exclusao = None

    @declared_attr
    def data_exclusao(cls):
        return Column(DateTime(timezone=False), nullable=True)

    def delete(self):
        self.data_exclusao = fortaleza_now

    def restore(self):
        self.data_exclusao = None

