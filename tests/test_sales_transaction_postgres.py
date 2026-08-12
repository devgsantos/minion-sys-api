import os
import threading
import unittest
import uuid
from datetime import datetime

from flask import Flask, request
from sqlalchemy import Column, DateTime, ForeignKey, Integer, create_engine, text
from sqlalchemy.orm import declarative_base, scoped_session, sessionmaker

from app.shared.helpers.model_operations import (
    InsufficientStockError,
    ModelOperations,
    SaleAlreadyExistsError,
)


Base = declarative_base()


class Product(Base):
    __tablename__ = 'test_product'
    produto_id = Column(Integer, primary_key=True)
    empresa_id = Column(Integer, nullable=False)
    data_exclusao = Column(DateTime)


class Budget(Base):
    __tablename__ = 'test_budget'
    orcamento_id = Column(Integer, primary_key=True)
    empresa_id = Column(Integer, nullable=False)
    orcamento_status_id = Column(Integer, nullable=False, default=1)
    venda_id = Column(Integer)
    data_aprovacao = Column(DateTime)
    data_exclusao = Column(DateTime)


class BudgetItem(Base):
    __tablename__ = 'test_budget_item'
    orcamento_item_id = Column(Integer, primary_key=True)
    orcamento_id = Column(Integer, ForeignKey('test_budget.orcamento_id'))
    produto_id = Column(Integer, ForeignKey('test_product.produto_id'))
    quantidade_orcamento = Column(Integer, nullable=False)
    data_exclusao = Column(DateTime)


class Stock(Base):
    __tablename__ = 'test_stock'
    estoque_id = Column(Integer, primary_key=True)
    produto_id = Column(Integer, ForeignKey('test_product.produto_id'))
    quantidade_disponivel = Column(Integer, nullable=False)
    data_exclusao = Column(DateTime)


class Sale(Base):
    __tablename__ = 'test_sale'
    venda_id = Column(Integer, primary_key=True)
    orcamento_id = Column(Integer, ForeignKey('test_budget.orcamento_id'))
    empresa_id = Column(Integer, nullable=False)
    data_exclusao = Column(DateTime)


@unittest.skipUnless(
    os.environ.get('TEST_DATABASE_URL'),
    'TEST_DATABASE_URL não configurada para testes PostgreSQL',
)
class SalesTransactionPostgresTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = f"minion_test_{uuid.uuid4().hex}"
        cls.engine = create_engine(os.environ['TEST_DATABASE_URL'])
        with cls.engine.begin() as connection:
            connection.execute(text(f'CREATE SCHEMA "{cls.schema}"'))
            connection.execute(text(f'SET search_path TO "{cls.schema}"'))
            Base.metadata.create_all(connection)
        cls.Session = scoped_session(sessionmaker(
            bind=cls.engine.execution_options(
                schema_translate_map={None: cls.schema},
            ),
            expire_on_commit=False,
        ))

    @classmethod
    def tearDownClass(cls):
        cls.Session.remove()
        with cls.engine.begin() as connection:
            connection.execute(text(f'DROP SCHEMA "{cls.schema}" CASCADE'))
        cls.engine.dispose()

    def setUp(self):
        session = self.Session()
        for model in (Sale, Stock, BudgetItem, Budget, Product):
            session.query(model).delete()
        session.add_all([
            Product(produto_id=1, empresa_id=10),
            Budget(orcamento_id=1, empresa_id=10, orcamento_status_id=1),
            BudgetItem(
                orcamento_item_id=1,
                orcamento_id=1,
                produto_id=1,
                quantidade_orcamento=3,
            ),
            Stock(estoque_id=1, produto_id=1, quantidade_disponivel=5),
        ])
        session.commit()
        self.app = Flask(__name__)

    def convert(self):
        with self.app.test_request_context('/venda'):
            request.db_session = self.Session
            return ModelOperations().create_sale_from_budget_atomic(
                Sale,
                {'orcamento_id': 1, 'empresa_id': 10},
                {},
                Budget,
                {'orcamento_id': 1, 'empresa_id': 10},
                {
                    'orcamento_status_id': 2,
                    'data_aprovacao': datetime.now(),
                    'venda_id': '$primary_id',
                },
                BudgetItem,
                Stock,
                Product,
                10,
            )

    def test_success_commits_sale_budget_and_stock_together(self):
        sale = self.convert()
        session = self.Session()
        self.assertIsNotNone(sale.venda_id)
        self.assertEqual(session.get(Stock, 1).quantidade_disponivel, 2)
        self.assertEqual(session.get(Budget, 1).venda_id, sale.venda_id)

    def test_insufficient_stock_rolls_back_every_change(self):
        session = self.Session()
        session.get(Stock, 1).quantidade_disponivel = 2
        session.commit()

        with self.assertRaises(InsufficientStockError):
            self.convert()

        session.expire_all()
        self.assertIsNone(session.query(Sale).one_or_none())
        self.assertEqual(session.get(Stock, 1).quantidade_disponivel, 2)
        self.assertIsNone(session.get(Budget, 1).venda_id)

    def test_concurrent_conversion_creates_one_sale_and_one_stock_debit(self):
        barrier = threading.Barrier(2)
        outcomes = []

        def worker():
            self.Session.remove()
            barrier.wait()
            try:
                self.convert()
                outcomes.append('created')
            except SaleAlreadyExistsError:
                outcomes.append('exists')
            finally:
                self.Session.remove()

        threads = [threading.Thread(target=worker) for _ in range(2)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=10)

        session = self.Session()
        self.assertEqual(sorted(outcomes), ['created', 'exists'])
        self.assertEqual(session.query(Sale).count(), 1)
        self.assertEqual(session.get(Stock, 1).quantidade_disponivel, 2)


if __name__ == '__main__':
    unittest.main()
