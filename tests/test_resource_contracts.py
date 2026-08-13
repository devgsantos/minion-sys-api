import unittest
from unittest.mock import MagicMock

from flask import Flask, request

from app.modules.product_category.product_category_usecase import ProductCategoryUseCase
from app.modules.service.service_usecase import ServiceUseCase
from app.modules.service_type.service_type_usecase import ServiceTypeUseCase


class ResourceContractTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)

    def assert_tenant_get_by_id(self, usecase, method_name, path, id_field):
        usecase.operations = MagicMock()
        usecase.operations.findOne.return_value = None
        usecase.logger = MagicMock()
        with self.app.test_request_context(path):
            request.company_id = 10
            response, status = getattr(usecase, method_name)()
        self.assertEqual(status, 404)
        self.assertFalse(response['status'])
        self.assertEqual(
            usecase.operations.findOne.call_args.kwargs,
            {id_field: '7', 'empresa_id': 10},
        )

    def test_service_by_id_is_tenant_scoped(self):
        usecase = ServiceUseCase.__new__(ServiceUseCase)
        usecase.service_model = object()
        self.assert_tenant_get_by_id(
            usecase,
            'get_service_by_id',
            '/servico/por_id?servico_id=7',
            'servico_id',
        )

    def test_service_type_by_id_is_tenant_scoped(self):
        usecase = ServiceTypeUseCase.__new__(ServiceTypeUseCase)
        usecase.service_type_model = object()
        self.assert_tenant_get_by_id(
            usecase,
            'get_service_type_by_id',
            '/servico-tipo/por_id?servico_tipo_id=7',
            'servico_tipo_id',
        )

    def test_product_category_by_id_is_tenant_scoped(self):
        usecase = ProductCategoryUseCase.__new__(ProductCategoryUseCase)
        usecase.product_category_model = object()
        self.assert_tenant_get_by_id(
            usecase,
            'get_product_category_by_id',
            '/produto-categoria/por_id?produto_categoria_id=7',
            'produto_categoria_id',
        )


if __name__ == '__main__':
    unittest.main()
