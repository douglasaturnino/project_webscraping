import time
from typing import Any, Dict

import requests
from bs4 import BeautifulSoup


class Scraper:
    @staticmethod
    def fetch_page() -> str:
        url = "https://www.mercadolivre.com.br/apple-iphone-16-pro-1-tb-titnio-preto-distribuidor-autorizado/p/MLB1040287851#polycard_client=search-nordic&wid=MLB5054621110&sid=search&searchVariation=MLB1040287851&position=3&search_layout=stack&type=product&tracking_id=98d5335b-6853-403d-9dd6-98374bef3f1b"
        response = requests.get(url)
        return response.text

    @staticmethod
    def parse_page(html: str) -> Dict[str, Any]:
        soup = BeautifulSoup(html, "html.parser")
        product_name = soup.find("h1", class_="ui-pdp-title").get_text(
            strip=True
        )
        prices = soup.find_all("span", class_="andes-money-amount__fraction")
        old_price = int(prices[0].get_text(strip=True).replace(".", ""))
        new_price = int(prices[1].get_text(strip=True).replace(".", ""))
        installment_price = int(
            prices[2].get_text(strip=True).replace(".", "")
        )
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        return {
            "product_name": product_name,
            "old_price": old_price,
            "new_price": new_price,
            "installment_price": installment_price,
            "timestamp": timestamp,
        }
