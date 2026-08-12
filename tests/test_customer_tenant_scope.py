import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from flask import Flask, request

from app.modules.customer.customer_usecase import CustomerUseCase


class CustomerTenantScopeTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.operations = MagicMock()
        self.functions = MagicMock()
        self.functions.token_decript.return_value = {'login_id': 7}

    def make_usecase(self):
        with (
            patch(
                'app.modules.customer.customer_usecase.ModelOperations',
                return_value=self.operations,
            ),
            patch(
                'app.modules.customer.customer_usecase.Functions',
                return_value=self.functions,
            ),
        ):
            return CustomerUseCase()

    def test_update_scopes_customer_by_authenticated_company(self):
        payload = self.customer_payload(cliente_id=9, empresa_id=20)
        self.operations.update_where.return_value = SimpleNamespace(cliente_id=9)

        with self.app.test_request_context('/cliente', method='PUT', json=payload):
            request.company_id = 10
            response, status = self.make_usecase().update_customer()

        self.assertEqual(status, 200)
        filters = self.operations.update_where.call_args.args[1]
        values = self.operations.update_where.call_args.kwargs
        self.assertEqual(filters, {'cliente_id': 9, 'empresa_id': 10})
        self.assertEqual(values['empresa_id'], 10)
        self.assertTrue(response['status'])

    def test_update_returns_404_for_customer_from_another_company(self):
        self.operations.update_where.return_value = None

        with self.app.test_request_context(
            '/cliente',
            method='PUT',
            json=self.customer_payload(cliente_id=9, empresa_id=10),
        ):
            request.company_id = 10
            response, status = self.make_usecase().update_customer()

        self.assertEqual(status, 404)
        self.assertFalse(response['status'])

    def test_create_uses_authenticated_company_instead_of_payload(self):
        self.operations.insert.return_value = SimpleNamespace(cliente_id=9)

        with self.app.test_request_context(
            '/cliente',
            method='POST',
            json=self.customer_payload(empresa_id=20),
        ):
            request.company_id = 10
            _, status = self.make_usecase().create_customer()

        self.assertEqual(status, 201)
        self.assertEqual(self.operations.insert.call_args.kwargs['empresa_id'], 10)

    @staticmethod
    def customer_payload(**overrides):
        payload = {
            'email': 'cliente@example.com',
            'nome': 'Cliente',
            'logradouro': 'Rua A',
            'numero_endereco': '1',
            'bairro': 'Centro',
            'cidade': 'Fortaleza',
            'uf': 'CE',
            'telefone': '85999999999',
            'cpf': None,
            'cnpj': None,
            'nacionalidade': 1,
            'naturalidade': 'Fortaleza',
            'empresa_id': 10,
        }
        payload.update(overrides)
        return payload


if __name__ == '__main__':
    unittest.main()
