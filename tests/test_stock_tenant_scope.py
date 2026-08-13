import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from flask import Flask, request

from app.modules.stock.stock_usecase import StockUseCase


class StockTenantScopeTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.operations = MagicMock()
        self.functions = MagicMock()
        self.functions.token_decript.return_value = {'login_id': 7}

    def make_usecase(self):
        with (
            patch(
                'app.modules.stock.stock_usecase.ModelOperations',
                return_value=self.operations,
            ),
            patch(
                'app.modules.stock.stock_usecase.Functions',
                return_value=self.functions,
            ),
        ):
            return StockUseCase()

    def test_list_filters_stock_through_product_company(self):
        self.operations.find_many_by_relation.return_value = ([], 0)

        with self.app.test_request_context('/estoque/todos?pagina=1&limite=10'):
            request.company_id = 10
            _, status = self.make_usecase().get_stock_all()

        self.assertEqual(status, 200)
        self.assertEqual(
            self.operations.find_many_by_relation.call_args.kwargs['empresa_id'],
            10,
        )

    def test_create_rejects_product_from_another_company(self):
        self.operations.findOne.return_value = None
        payload = {
            'produto_id': 99,
            'estoque_tipo_id': 1,
            'quantidade_disponivel': 5,
        }

        with self.app.test_request_context('/estoque', method='POST', json=payload):
            request.company_id = 10
            _, status = self.make_usecase().create_stock()

        self.assertEqual(status, 400)
        self.operations.insert.assert_not_called()
        self.operations.findOne.assert_called_once_with(
            self.make_usecase().product_model,
            produto_id=99,
            empresa_id=10,
        )

    def test_get_by_id_hides_stock_from_another_company(self):
        stock = SimpleNamespace(estoque_id=5, produto_id=99)
        self.operations.findOne.side_effect = [stock, None]

        with self.app.test_request_context('/estoque/por_id?estoque_id=5'):
            request.company_id = 10
            response, status = self.make_usecase().get_stock_by_id()

        self.assertEqual(status, 404)
        self.assertFalse(response['status'])

    def test_budget_stock_check_uses_tenant_and_budget_quantity(self):
        budget = SimpleNamespace(orcamento_id=5)
        product = SimpleNamespace(produto_id=9)
        item = SimpleNamespace(produto_id=9, quantidade_orcamento=3)
        stock = SimpleNamespace(produto_id=9, quantidade_disponivel=2)
        self.operations.findOne.side_effect = [budget, product]
        self.operations.findManyNoffset.side_effect = [([item], 1), ([stock], 1)]

        with self.app.test_request_context('/estoque/verificar?orcamento_id=5'):
            request.company_id = 10
            response = self.make_usecase().check_stock_by_product(5)

        self.assertFalse(response['status'])
        self.assertEqual(
            response['data']['produtos_insuficientes'][0]['quantidade_necessaria'],
            3,
        )
        self.assertEqual(
            self.operations.findOne.call_args_list[0].kwargs,
            {'orcamento_id': 5, 'empresa_id': 10},
        )


if __name__ == '__main__':
    unittest.main()
