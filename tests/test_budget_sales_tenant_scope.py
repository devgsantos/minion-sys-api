import unittest
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from flask import Flask, request

from app.modules.budget.budget_usecase import BudgetUseCase
from app.modules.sales.sales_usecase import SalesUseCase
from app.shared.helpers.model_operations import InsufficientStockError


class BudgetSalesTenantScopeTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.operations = MagicMock()
        self.functions = MagicMock()
        self.functions.token_decript.return_value = {'login_id': 7}

    def make_budget_usecase(self):
        with (
            patch(
                'app.modules.budget.budget_usecase.ModelOperations',
                return_value=self.operations,
            ),
            patch(
                'app.modules.budget.budget_usecase.Functions',
                return_value=self.functions,
            ),
        ):
            return BudgetUseCase()

    def make_sales_usecase(self):
        with (
            patch(
                'app.modules.sales.sales_usecase.ModelOperations',
                return_value=self.operations,
            ),
            patch(
                'app.modules.sales.sales_usecase.Functions',
                return_value=self.functions,
            ),
        ):
            return SalesUseCase()

    def test_budget_value_uses_quantity_and_company_filter(self):
        product = SimpleNamespace(produto_id=5, preco_venda=Decimal('12.50'))
        self.operations.findManyNoffset.return_value = ([product], 1)

        with self.app.test_request_context('/orcamento'):
            request.company_id = 10
            total = self.make_budget_usecase().calculate_items_value(
                [{'produto_id': 5, 'quantidade_orcamento': 3}],
                [],
            )

        self.assertEqual(total, Decimal('37.50'))
        self.assertEqual(
            self.operations.findManyNoffset.call_args.kwargs['empresa_id'],
            10,
        )

    def test_budget_rejects_item_from_another_company(self):
        self.operations.findManyNoffset.return_value = ([], 0)

        with self.app.test_request_context('/orcamento'):
            request.company_id = 10
            with self.assertRaisesRegex(ValueError, 'produtos'):
                self.make_budget_usecase().calculate_items_value(
                    [{'produto_id': 99, 'quantidade_orcamento': 1}],
                    [],
                )

    def test_budget_rejects_customer_from_another_company(self):
        self.operations.findOne.return_value = None
        payload = {
            'orcamento_id': None,
            'cliente_id': 99,
            'empresa_id': 20,
            'orcamento_itens': [{'produto_id': 5, 'quantidade_orcamento': 1}],
        }

        with self.app.test_request_context('/orcamento', method='POST', json=payload):
            request.company_id = 10
            response, status = self.make_budget_usecase().save_budget()

        self.assertEqual(status, 404)
        self.assertFalse(response['status'])
        self.operations.merge_insert_if_not_exists.assert_not_called()

    def test_sale_rejects_budget_from_another_company(self):
        self.operations.findOne.return_value = None
        payload = {'orcamento_id': 99, 'empresa_id': 20, 'gera_ordem_servico': False}

        with self.app.test_request_context('/venda', method='POST', json=payload):
            request.company_id = 10
            response, status = self.make_sales_usecase().save_sale()

        self.assertEqual(status, 404)
        self.assertFalse(response['status'])
        self.operations.merge_insert_if_not_exists.assert_not_called()

    def test_get_sale_by_id_uses_company_filter(self):
        self.operations.findOne.return_value = None

        with self.app.test_request_context('/venda/por_id?venda_id=5'):
            request.company_id = 10
            _, status = self.make_sales_usecase().get_by_id()

        self.assertEqual(status, 404)
        self.operations.findOne.assert_called_once_with(
            self.make_sales_usecase().sales_model,
            venda_id='5',
            empresa_id=10,
        )

    def test_approved_budget_conversion_uses_single_atomic_operation(self):
        budget = SimpleNamespace(
            orcamento_id=5,
            empresa_id=10,
            orcamento_status_id=1,
            data_cadastro=None,
            valor=Decimal('100.00'),
            desconto=Decimal('10.00'),
        )
        sale = SimpleNamespace(venda_id=8)
        self.operations.findOne.side_effect = [budget, None]
        self.operations.create_sale_from_budget_atomic.return_value = sale
        payload = {
            'orcamento_id': 5,
            'empresa_id': 10,
            'gera_ordem_servico': False,
        }

        serialized = MagicMock()
        serialized.dict.return_value = {'venda_id': 8}
        with (
            self.app.test_request_context('/venda', method='POST', json=payload),
            patch(
                'app.modules.sales.sales_usecase.VendaBaseModel.from_orm',
                return_value=serialized,
            ),
        ):
            request.company_id = 10
            response, status = self.make_sales_usecase().save_sale()

        self.assertEqual(status, 201)
        self.assertTrue(response['status'])
        self.operations.create_sale_from_budget_atomic.assert_called_once()
        self.operations.merge_insert_if_not_exists.assert_not_called()
        self.operations.update_where.assert_not_called()

    def test_insufficient_stock_returns_conflict(self):
        budget = SimpleNamespace(
            orcamento_id=5,
            empresa_id=10,
            orcamento_status_id=1,
            data_cadastro=None,
            valor=Decimal('100.00'),
            desconto=Decimal('0.00'),
        )
        self.operations.findOne.side_effect = [budget, None]
        self.operations.create_sale_from_budget_atomic.side_effect = (
            InsufficientStockError([{
                'produto_id': 9,
                'quantidade_necessaria': 3,
                'quantidade_disponivel': 1,
            }])
        )
        payload = {
            'orcamento_id': 5,
            'empresa_id': 10,
            'gera_ordem_servico': False,
        }

        with self.app.test_request_context('/venda', method='POST', json=payload):
            request.company_id = 10
            response, status = self.make_sales_usecase().save_sale()

        self.assertEqual(status, 409)
        self.assertFalse(response['status'])
        self.assertEqual(response['data']['produtos_insuficientes'][0]['produto_id'], 9)


if __name__ == '__main__':
    unittest.main()
