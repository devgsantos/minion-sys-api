import unittest
from datetime import datetime
from unittest.mock import MagicMock
from unittest.mock import patch

from flask import Flask, request
from sqlalchemy import Column, DateTime, Integer, create_engine
from sqlalchemy.orm import declarative_base, scoped_session, sessionmaker

from app.modules.budget.budget_usecase import BudgetUseCase
from app.modules.sales.sales_usecase import SalesUseCase
from app import register_error_handlers
from app.shared.helpers.http import InvalidPaginationError, parse_pagination
from app.shared.helpers.http import INTERNAL_ERROR_MESSAGE, error_payload
from app.shared.helpers.model_operations import ModelOperations


Base = declarative_base()


class Record(Base):
    __tablename__ = 'contract_record'
    contract_record_id = Column(Integer, primary_key=True)
    venda_id = Column(Integer)
    data_cadastro = Column(DateTime, default=datetime.now)
    data_exclusao = Column(DateTime)


class HttpContractTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)

    def test_pagination_rejects_invalid_values(self):
        with self.app.test_request_context('/?pagina=0&limite=10'):
            with self.assertRaises(InvalidPaginationError):
                parse_pagination(request.args)
        with self.app.test_request_context('/?pagina=1&limite=101'):
            with self.assertRaises(InvalidPaginationError):
                parse_pagination(request.args)

    def test_sales_list_returns_400_for_invalid_pagination(self):
        with self.app.test_request_context('/venda/todos?pagina=x'):
            response, status = SalesUseCase.__new__(SalesUseCase).get_all_sales()
        self.assertEqual(status, 400)
        self.assertFalse(response['status'])

    def test_sales_internal_error_does_not_leak_details(self):
        usecase = SalesUseCase.__new__(SalesUseCase)
        usecase.sales_model = object()
        usecase.operations = MagicMock()
        usecase.operations.findOne.side_effect = RuntimeError('database secret')
        usecase.logger = MagicMock()

        with self.app.test_request_context('/venda/por_id?venda_id=1'):
            request.company_id = 10
            response, status = usecase.get_by_id()

        self.assertEqual(status, 500)
        self.assertEqual(response['message'], INTERNAL_ERROR_MESSAGE)
        self.assertNotIn('secret', response['message'])

    def test_budget_list_applies_sale_filter_in_query(self):
        usecase = BudgetUseCase.__new__(BudgetUseCase)
        usecase.budget_model = object()
        usecase.operations = MagicMock()
        usecase.operations.findMany.return_value = ([], 0)

        with self.app.test_request_context('/orcamento/todos?venda=true'):
            request.company_id = 10
            response, status = usecase.get_all_budgets()

        self.assertEqual(status, 200)
        self.assertEqual(response['data']['total'], 0)
        self.assertEqual(
            usecase.operations.findMany.call_args.kwargs['venda_id'],
            ('is_not', None),
        )

    def test_find_many_counts_only_filtered_rows(self):
        engine = create_engine('sqlite://')
        Base.metadata.create_all(engine)
        Session = scoped_session(sessionmaker(bind=engine))
        session = Session()
        session.add_all([Record(venda_id=1), Record(venda_id=None)])
        session.commit()

        with self.app.test_request_context('/'):
            request.db_session = Session
            records, total = ModelOperations().findMany(
                Record,
                venda_id=('is_not', None),
            )

        self.assertEqual(total, 1)
        self.assertEqual([record.venda_id for record in records], [1])
        Session.remove()
        engine.dispose()

    def test_error_payload_does_not_require_exception_details(self):
        payload = error_payload(INTERNAL_ERROR_MESSAGE)
        self.assertEqual(payload['message'], 'Erro interno do servidor.')
        self.assertIsNone(payload['data'])

    def test_unexpected_error_hides_exception_details(self):
        app = Flask(__name__)
        app.config['TESTING'] = False
        register_error_handlers(app)

        @app.get('/failure')
        def failure():
            raise RuntimeError('database password leaked')

        with patch('app.Logger'):
            response = app.test_client().get('/failure')

        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.get_json()['message'], INTERNAL_ERROR_MESSAGE)
        self.assertNotIn('password', response.get_data(as_text=True))

    def test_http_error_preserves_status_in_standard_envelope(self):
        app = Flask(__name__)
        register_error_handlers(app)
        response = app.test_client().get('/missing')
        self.assertEqual(response.status_code, 404)
        self.assertFalse(response.get_json()['status'])


if __name__ == '__main__':
    unittest.main()
