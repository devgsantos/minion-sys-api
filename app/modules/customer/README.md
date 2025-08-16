# Customer Module

This module provides API endpoints for managing customers.

## Endpoints

### GET /cliente/todos
Retrieves all customers with pagination support.

Query Parameters:
- `empresa_id` (required): ID of the company
- `pagina` (optional): Page number for pagination (default: 1)
- `limite` (optional): Number of items per page (default: 10)
- `termo_pesquisa` (optional): Search term to filter customers

### GET /cliente/por_id
Retrieves a customer by ID.

Query Parameters:
- `empresa_id` (required): ID of the company
- `cliente_id` (required): ID of the customer to retrieve

### POST /cliente
Creates a new customer.

Required JSON body:
```json
{
  "email": "email@example.com",
  "nome": "Nome do Cliente",
  "logradouro": "Endereço do Cliente",
  "numero_endereco": "123",
  "bairro": "Bairro",
  "cidade": "Cidade",
  "uf": "UF",
  "telefone": "123456789",
  "cpf": "12345678901",  // Optional
  "cnpj": "12345678901234",  // Optional
  "nacionalidade": 1,  // País ID
  "naturalidade": "Cidade de Nascimento",
  "empresa_id": 1
}
```

### PUT /cliente
Updates an existing customer.

Required JSON body:
```json
{
  "cliente_id": 1,  // Required
  "email": "email@example.com",
  "nome": "Nome do Cliente",
  "logradouro": "Endereço do Cliente",
  "numero_endereco": "123",
  "bairro": "Bairro",
  "cidade": "Cidade",
  "uf": "UF",
  "telefone": "123456789",
  "cpf": "12345678901",  // Optional
  "cnpj": "12345678901234",  // Optional
  "nacionalidade": 1,  // País ID
  "naturalidade": "Cidade de Nascimento",
  "empresa_id": 1
}
```

### DELETE /cliente
Soft deletes a customer.

Query Parameters:
- `empresa_id` (required): ID of the company
- `cliente_id` (required): ID of the customer to delete
