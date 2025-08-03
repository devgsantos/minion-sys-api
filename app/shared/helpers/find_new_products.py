import requests
from flask import request

from app.shared.singletons.logger import Logger

from bs4 import BeautifulSoup
import urllib.parse
import random
import time
import base64
from io import BytesIO

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import urllib.parse
import time
import random


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
    

    def find_new_products_product_search_net(self, ean: str) -> dict | None:
        try:
            # 1. Acessar site
            search_url = f"https://pt.product-search.net/?q={ean}"
            headers = {"User-Agent": self.random_user_agent()}
            response = requests.get(search_url, headers=headers, timeout=5)
            if response.status_code != 200:
                return None

            soup = BeautifulSoup(response.text, 'html.parser')
            block = soup.find("div", class_="col-xs-12 col-md-7")
            if not block:
                return None

            a_tag = block.find("a")


            # 2. Buscar imagem no Bing ou Google e converter para base64
           
            imagem_url, titulo_bing = self.buscar_imagem_bing(ean)

            if not imagem_url:
                imagem_url, titulo_google = self.buscar_imagem_google(ean)


            imagem_base64 = self.baixar_imagem_base64(imagem_url) if imagem_url else None

            titulo = a_tag.text.strip() or titulo_google or titulo_bing

            if not titulo or not imagem_base64:
                return {
                    "status": False,
                    "message": "Produto não encontrado.",
                    "data": None
                }, 404
            return {
                "titulo": titulo,
                "imagem": imagem_base64
            }

        except Exception as exc:
            self.logger.log(message=str(exc), level='error')
            return {
                "status": False,
                "message": f"Erro inesperado: {str(exc)}",
                "data": None
            }, 500

    # Ajustar o Google, pois às vezes não acha a classe da div de imagem
    # grande. Adicionar verificação se a imagem existe na aba original se não
    # buscar a imagem na aba ampliada.
    def buscar_imagem_google(self, termo: str) -> str | None:
        try:
            query = urllib.parse.quote(termo)
            url = f"https://www.google.com/search?q={query}&tbm=isch"

            chrome_options = Options()
            chrome_options.add_argument("--headless=new")  # Headless moderno do Chrome
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option("useAutomationExtension", False)
            chrome_options.add_argument(f"user-agent={self.random_user_agent()}")

            driver = webdriver.Chrome(options=chrome_options)

            # Evasão: remove webdriver do JS
            driver.execute_cdp_cmd(
                "Page.addScriptToEvaluateOnNewDocument",
                {
                    "source": """
                        Object.defineProperty(navigator, 'webdriver', {
                            get: () => undefined
                        });
                        window.navigator.chrome = {
                            runtime: {}
                        };
                        Object.defineProperty(navigator, 'languages', {
                            get: () => ['pt-BR', 'pt']
                        });
                        Object.defineProperty(navigator, 'plugins', {
                            get: () => [1, 2, 3]
                        });
                    """
                }
            )

            driver.get(url)
            wait = WebDriverWait(driver, 10)

            # Clica na primeira imagem visível
            thumb = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "img.YQ4gaf")))
            time.sleep(random.uniform(1.2, 2.2))
            alt_text = ""
            try:
                alt_element = driver.find_element(By.CLASS_NAME, "toI8Rb")
                alt_text = alt_element.text.strip()
            except:
                alt_text = ""
            actions = ActionChains(driver)
            actions.key_down(Keys.CONTROL).click(thumb).key_up(Keys.CONTROL).perform()
            original_window = driver.current_window_handle
            wait.until(EC.number_of_windows_to_be(2))
            for handle in driver.window_handles:
                if handle != original_window:
                    driver.switch_to.window(handle)
                    break

            # Aguarda carregar as imagens ampliadas

            img = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "img.sFlh5c")))
            src = img.get_attribute("src")
            driver.quit()
            if src and src.startswith("http"):
                return src, alt_text
            return None, alt_text

        except Exception as exc:
            self.logger.log(message=f"[Google Headless Error] {exc}", level='error')
            return None, ""
        

    def buscar_imagem_bing(self, termo: str) -> tuple[str | None, str]:
        try:
            query = urllib.parse.quote(termo)
            url = f"https://www.bing.com/images/search?q={query}"

            chrome_options = Options()
            chrome_options.add_argument("--headless=new")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option("useAutomationExtension", False)
            chrome_options.add_argument(f"user-agent={self.random_user_agent()}")

            driver = webdriver.Chrome(options=chrome_options)

            # Evasão mínima
            driver.execute_cdp_cmd(
                "Page.addScriptToEvaluateOnNewDocument",
                {
                    "source": """
                        Object.defineProperty(navigator, 'webdriver', {
                            get: () => undefined
                        });
                    """
                }
            )

            driver.get(url)
            wait = WebDriverWait(driver, 10)

            # Aguarda o primeiro bloco de imagem (a tag que abre o detalhe)
            thumb = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.iusc")))
            time.sleep(random.uniform(1.2, 2.2))

            # Busca título alternativo (fallback) dentro do bloco
            titulo_fallback = ""
            try:
                data_list = thumb.find_element(By.XPATH, ".//following-sibling::ul[contains(@class, 'b_dataList')]")
                a_tag = data_list.find_element(By.TAG_NAME, "a")
                titulo_fallback = a_tag.get_attribute("title") or a_tag.text.strip()
            except Exception:
                titulo_fallback = ""

            # Ctrl+Click para abrir imagem ampliada em nova aba
            actions = ActionChains(driver)
            actions.key_down(Keys.CONTROL).click(thumb).key_up(Keys.CONTROL).perform()
            original_window = driver.current_window_handle

            wait.until(EC.number_of_windows_to_be(2))
            for handle in driver.window_handles:
                if handle != original_window:
                    driver.switch_to.window(handle)
                    break

            # Aguarda imagem grande
            img = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "img.nofocus")))
            src = img.get_attribute("src")
            driver.quit()

            if src and src.startswith("http"):
                return src, titulo_fallback
            return None, titulo_fallback

        except Exception as exc:
            self.logger.log(message=f"[Bing Image Error] {exc}", level='error')
            return None, ""


    def baixar_imagem_base64(self, url: str) -> str | None:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code != 200:
                return None

            buffer = BytesIO(response.content)
            encoded_string = base64.b64encode(buffer.getvalue()).decode("utf-8")
            return f"data:image/jpeg;base64,{encoded_string}"

        except Exception:
            return None


    def random_user_agent(self) -> str:
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:100.0)",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X)",
            "Mozilla/5.0 (Linux; Android 10; SM-A205G)"
        ]
        return random.choice(user_agents)
