# Documentação - Campo Imagem Atualizado (Formato Estruturado)

O campo `imagem` no `ProdutoRequestModel` foi atualizado para receber um objeto estruturado com informações específicas para upload, proporcionando maior controle sobre o processamento de imagens.

## Novo Formato do Campo Imagem

### Estrutura Obrigatória:
```typescript
interface ImagemProduto {
  tipo: string;        // Tipo da imagem (ex: "produto")
  arquivo: string;     // Dados da imagem em base64
  nome_arquivo: string; // Nome do arquivo com extensão
}
```

### Exemplo de Requisição:
```json
{
  "titulo": "Produto Exemplo",
  "sku": "PROD001",
  "preco_custo": 10.50,
  "preco_venda": 25.00,
  "imagem": {
    "tipo": "produto",
    "arquivo": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAYABgAAD...",
    "nome_arquivo": "produto_123.jpg"
  },
  "produto_categoria_id": 1,
  "produto_subcategoria_id": 1,
  "produto_tipo_id": 1,
  "empresa_id": 1
}
```

## Validações Aplicadas

### Campo Opcional:
- `imagem` é **opcional** - pode ser `null` ou omitido

### Quando fornecido, deve conter:
- ✅ `tipo` (string, não vazio)
- ✅ `arquivo` (string, não vazio) - base64 da imagem
- ✅ `nome_arquivo` (string, não vazio) - nome com extensão

### Validações automáticas:
- Verificação de estrutura do objeto
- Validação de tipos (todos devem ser string)
- Verificação de campos obrigatórios
- Validação de conteúdo não vazio

## Processamento Automático

Quando uma imagem é fornecida no novo formato:

1. **Validação** da estrutura do objeto imagem
2. **Upload** automático via `FileRepositoryUseCase`
3. **Processamento** com PIL (redimensionamento, conversão)
4. **Organização** em estrutura de pastas por empresa/tipo
5. **Atualização** do campo imagem com o caminho resultante

## Exemplos de Uso

### JavaScript/TypeScript
```javascript
const criarProdutoComImagem = async (dadosProduto, imagemFile) => {
  // Converter arquivo para base64
  const base64 = await fileToBase64(imagemFile);
  
  const produto = {
    titulo: dadosProduto.titulo,
    sku: dadosProduto.sku,
    preco_custo: dadosProduto.preco_custo,
    preco_venda: dadosProduto.preco_venda,
    imagem: {
      tipo: "produto",
      arquivo: base64,
      nome_arquivo: imagemFile.name
    },
    produto_categoria_id: dadosProduto.produto_categoria_id,
    produto_subcategoria_id: dadosProduto.produto_subcategoria_id,
    produto_tipo_id: dadosProduto.produto_tipo_id,
    empresa_id: dadosProduto.empresa_id
  };
  
  const response = await fetch('/produto', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-auth-token': token
    },
    body: JSON.stringify(produto)
  });
  
  return await response.json();
};

// Função auxiliar para converter arquivo para base64
const fileToBase64 = (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => resolve(reader.result);
    reader.onerror = error => reject(error);
  });
};
```

### Python
```python
import base64
import requests

def criar_produto_com_imagem(dados_produto, caminho_imagem, token):
    # Ler e codificar imagem
    with open(caminho_imagem, 'rb') as img_file:
        img_data = base64.b64encode(img_file.read()).decode('utf-8')
    
    # Estruturar dados do produto
    produto = {
        "titulo": dados_produto["titulo"],
        "sku": dados_produto["sku"],
        "preco_custo": dados_produto["preco_custo"],
        "preco_venda": dados_produto["preco_venda"],
        "imagem": {
            "tipo": "produto",
            "arquivo": f"data:image/jpeg;base64,{img_data}",
            "nome_arquivo": dados_produto["nome_arquivo"]
        },
        "produto_categoria_id": dados_produto["produto_categoria_id"],
        "produto_subcategoria_id": dados_produto["produto_subcategoria_id"],
        "produto_tipo_id": dados_produto["produto_tipo_id"],
        "empresa_id": dados_produto["empresa_id"]
    }
    
    # Fazer requisição
    response = requests.post(
        'http://localhost:5000/produto',
        json=produto,
        headers={
            'Content-Type': 'application/json',
            'x-auth-token': token
        }
    )
    
    return response.json()
```

### Curl
```bash
curl -X POST http://localhost:5000/produto \
  -H "Content-Type: application/json" \
  -H "x-auth-token: seu_token" \
  -d '{
    "titulo": "Produto com Imagem",
    "sku": "PROD001",
    "preco_custo": 15.50,
    "preco_venda": 35.00,
    "imagem": {
      "tipo": "produto",
      "arquivo": "data:image/jpeg;base64,/9j/4AAQ...",
      "nome_arquivo": "produto_exemplo.jpg"
    },
    "produto_categoria_id": 1,
    "produto_subcategoria_id": 1,
    "produto_tipo_id": 1,
    "empresa_id": 1
  }'
```

## Possíveis Erros

### Estrutura inválida (400)
```json
{
  "status": false,
  "message": "Campo imagem deve ter a estrutura: {tipo: str, arquivo: str, nome_arquivo: str}",
  "data": null
}
```

### Campos obrigatórios faltando (400)
```json
{
  "status": false,
  "message": "Dados inválidos: Campos obrigatórios faltando em imagem: {'arquivo'}",
  "data": null
}
```

### Erro no upload (400)
```json
{
  "status": false,
  "message": "Erro no upload da imagem: Erro ao decodificar base64: Invalid base64-encoded string",
  "data": null
}
```

## Compatibilidade com Versão Anterior

O sistema mantém **compatibilidade com strings simples** para o campo imagem:

```json
{
  "titulo": "Produto Compatível",
  "imagem": "caminho/para/imagem.jpg",
  // ... outros campos
}
```

## Vantagens do Novo Formato

✅ **Controle total** sobre o tipo e nome do arquivo  
✅ **Upload automático** integrado ao processo de criação  
✅ **Validação robusta** da estrutura de dados  
✅ **Processamento padronizado** via FileRepository  
✅ **Organização automática** em estrutura de pastas  
✅ **Compatibilidade** com sistema legado  

## Fluxo de Processamento

1. **Recepção** do JSON com estrutura de imagem
2. **Validação** via Pydantic dos campos obrigatórios
3. **Upload** automático via `FileRepositoryUseCase.upload_image_str`
4. **Processamento** da imagem (redimensionamento, conversão)
5. **Armazenamento** em estrutura de pastas organizada
6. **Atualização** do campo imagem com caminho final
7. **Criação/Atualização** do produto no banco

Este novo formato oferece maior flexibilidade e controle sobre o upload de imagens, mantendo a simplicidade de uso através de uma única requisição JSON.
