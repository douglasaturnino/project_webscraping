import time
from typing import Any, Dict

import requests
from bs4 import BeautifulSoup


class Scraper:
    def __init__(self, url):
        self.url = url

    def fetch_page(self) -> str:
        url = self.url
        response = requests.get(url)
        return response.text

    @staticmethod
    def parse_page(html: str) -> Dict[str, Any]:
        soup = BeautifulSoup(html, "html.parser")
        product_name = soup.find("h1", class_="ui-pdp-title").get_text(
            strip=True
        )
        price_elements = soup.find_all(
            "span",
            class_="andes-money-amount ui-pdp-price__part andes-money-amount--cents-superscript andes-money-amount--compact",
        )

        prices = []
        for element in price_elements:
            fraction = element.find(
                "span", class_="andes-money-amount__fraction"
            )
            if fraction:
                prices.append(fraction.text)

        new_price = int(prices[0].replace(".", ""))
        if len(prices) > 1:
            installment_price = int(prices[1].replace(".", ""))
        if len(prices) > 2:
            old_price = int(prices[2].replace(".", ""))
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        return {
            "product_name": product_name,
            "old_price": old_price,
            "new_price": new_price,
            "installment_price": installment_price,
            "timestamp": timestamp,
        }
