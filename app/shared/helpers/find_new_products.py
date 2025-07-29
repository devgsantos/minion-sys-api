import requests
from flask import request

from app.shared.singletons.logger import Logger


class FindNewProducts:
    def __init__(self):
        self.logger = Logger()

    def find_new_products_openfoodfacts(self):
        try:
            url = f"https://world.openfoodfacts.org/api/v0/product/{request.args.get('ean')}.json"
            response = requests.get(url, timeout=5)
            if response.status_code != 200:
                return None

            data = response.json()
            product = data.get("product", {})
            if not product or data.get("status") != 1:
                return None

            return {
                "titulo": product.get("product_name", "").strip(),
                "descricao": product.get("ingredients_text", "").strip(),
                "marca": product.get("brands", "").strip(),
                "imagem": product.get("image_url", "").strip(),
                "categorias": product.get("categories", "").strip()
            }

        except Exception as exc:
            self.logger.log(message=str(exc), level='error')
            return {
                "status": False,
                "message": f"Erro inesperado: {str(exc)}",
                "result": None
            }, 500
        
    def find_new_products_upcitemdb(self):
        try:
            # ⚠️ Troque pela sua chave da UPCItemDB
            API_KEY = "trial"  # ou a sua chave real
            url = f"https://api.upcitemdb.com/prod/trial/lookup?upc={request.args.get('ean') }"
            headers = {"Content-Type": "application/json"}

            response = requests.get(url, headers=headers, timeout=5)

            if response.status_code != 200:
                return None

            data = response.json()
            items = data.get("items", [])

            if not items:
                return None

            item = items[0]
            return {
                "titulo": item.get("title", "").strip(),
                "descricao": item.get("description", "").strip(),
                "marca": item.get("brand", "").strip(),
                "imagem": item.get("images", [None])[0],
                "categorias": ", ".join(item.get("category", [])) if isinstance(item.get("category"), list) else item.get("category", "")
            }
        
        except Exception as exc:
            self.logger.log(message=str(exc), level='error')
            return {
                "status": False,
                "message": f"Erro inesperado: {str(exc)}",
                "result": None
            }, 500
        
    def find_new_products_mercadolivre(self):
        try:
            url = f"https://api.mercadolibre.com/sites/MLB/search?q={ean}"
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(url, headers=headers, timeout=5)

            if response.status_code != 200:
                return None

            results = response.json().get("results", [])
            if not results:
                return None

            produto = results[0]
            return {
                "titulo": produto.get("title", "").strip(),
                "descricao": produto.get("subtitle", "") or "",  # subtitle pode estar vazio
                "fonte": "Mercado Livre"
            }

        except Exception:
            return None