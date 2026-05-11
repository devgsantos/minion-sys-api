# Documentação - Campo Imagem no ProdutoRequestModel

O campo `imagem` no modelo `ProdutoRequestModel` foi atualizado para aceitar tanto **strings** (base64/URL) quanto **arquivos** (FileStorage), proporcionando flexibilidade no envio de imagens.

## Formatos Aceitos

### 1. String Base64
```json
{
  "titulo": "Produto Exemplo",
  "sku": "PROD001",
  "preco_custo": 10.50,
  "preco_venda": 25.00,
  "imagem": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAYABgAAD...",
  "produto_categoria_id": 1,
  "produto_subcategoria_id": 1,
  "produto_tipo_id": 1,
  "empresa_id": 1
}
```

### 2. String Base64 Simples (sem prefixo)
```json
{
  "titulo": "Produto Exemplo",
  "sku": "PROD001",
  "imagem": "/9j/4AAQSkZJRgABAQEAYABgAAD..."
}
```
> **Nota:** O sistema adicionará automaticamente o prefixo `data:image/jpeg;base64,`

### 3. Upload de Arquivo via Form-Data

#### Endpoints especiais para upload:
- **POST** `/produto/upload` - Criar produto com arquivo
- **PUT** `/produto/upload` - Atualizar produto com arquivo

#### Exemplo de requisição form-data:
```javascript
const formData = new FormData();
formData.append('titulo', 'Produto com Imagem');
formData.append('sku', 'PROD002');
formData.append('preco_custo', '15.00');
formData.append('preco_venda', '35.00');
formData.append('produto_categoria_id', '1');
formData.append('produto_subcategoria_id', '1');
formData.append('produto_tipo_id', '1');
formData.append('empresa_id', '1');
formData.append('imagem', fileInput.files[0]); // Arquivo selecionado

fetch('/produto/upload', {
  method: 'POST',
  headers: {
    'x-auth-token': 'seu_token_aqui'
  },
  body: formData
});
```

## Validações de Arquivo

### Tipos Permitidos:
- JPEG/JPG
- PNG
- GIF
- WebP
- BMP

### Restrições:
- **Tamanho máximo:** 5MB
- **Redimensionamento automático:** 800x600px (mantém proporção)
- **Qualidade JPEG:** 85% (para otimização)
- **Formato de saída:** JPEG com base64

## Processamento Automático

Quando um arquivo é enviado, o sistema:

1. **Valida** o tipo e tamanho do arquivo
2. **Converte** para RGB se necessário
3. **Redimensiona** mantendo a proporção
4. **Comprime** com qualidade 85%
5. **Converte** para base64
6. **Armazena** no formato `data:image/jpeg;base64,{dados}`

## Exemplos de Uso

### Frontend (JavaScript/TypeScript)

```typescript
// Enviando string base64
const produto = {
  titulo: 'Produto Base64',
  imagem: 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...',
  // ... outros campos
};

fetch('/produto', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'x-auth-token': token
  },
  body: JSON.stringify(produto)
});

// Enviando arquivo
const formData = new FormData();
formData.append('titulo', 'Produto com Arquivo');
formData.append('imagem', fileInput.files[0]);
// ... outros campos

fetch('/produto/upload', {
  method: 'POST',
  headers: {
    'x-auth-token': token
  },
  body: formData
});
```

### Curl (Terminal)

```bash
# Enviando JSON com base64
curl -X POST http://localhost:5000/produto \
  -H "Content-Type: application/json" \
  -H "x-auth-token: seu_token" \
  -d '{
    "titulo": "Produto Base64",
    "imagem": "data:image/jpeg;base64,/9j/4AAQ...",
    "sku": "PROD001",
    "preco_custo": 10.50,
    "preco_venda": 25.00,
    "produto_categoria_id": 1,
    "produto_subcategoria_id": 1,
    "produto_tipo_id": 1,
    "empresa_id": 1
  }'

# Enviando arquivo
curl -X POST http://localhost:5000/produto/upload \
  -H "x-auth-token: seu_token" \
  -F "titulo=Produto com Arquivo" \
  -F "sku=PROD002" \
  -F "preco_custo=15.00" \
  -F "preco_venda=35.00" \
  -F "produto_categoria_id=1" \
  -F "produto_subcategoria_id=1" \
  -F "produto_tipo_id=1" \
  -F "empresa_id=1" \
  -F "imagem=@/caminho/para/imagem.jpg"
```

## Tratamento de Erros

### Possíveis erros:
- `400` - Arquivo de imagem inválido
- `400` - Arquivo muito grande (> 5MB)  
- `400` - Erro ao processar imagem
- `400` - Dados inválidos na validação

### Exemplo de resposta de erro:
```json
{
  "status": false,
  "message": "Arquivo muito grande. Máximo permitido: 5MB",
  "data": null
}
```

## Migração de Código Existente

O código existente **continuará funcionando** sem alterações. A nova funcionalidade é **totalmente compatível** com implementações que enviam strings base64.
