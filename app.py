import asyncio
import time

import requests
from bs4 import BeautifulSoup

from config import Config as config
from database import Database
from telegram_bot import TelegramBot


def fetch_page():
    url = "https://www.mercadolivre.com.br/apple-iphone-16-pro-1-tb-titnio-preto-distribuidor-autorizado/p/MLB1040287851#polycard_client=search-nordic&wid=MLB5054621110&sid=search&searchVariation=MLB1040287851&position=3&search_layout=stack&type=product&tracking_id=98d5335b-6853-403d-9dd6-98374bef3f1b"
    response = requests.get(url)
    return response.text


def parse_page(html):
    soup = BeautifulSoup(html, "html.parser")
    product_name = soup.find("h1", class_="ui-pdp-title").get_text(strip=True)
    prices = soup.find_all("span", class_="andes-money-amount__fraction")
    old_price = int(prices[0].get_text(strip=True).replace(".", ""))
    new_price = int(prices[1].get_text(strip=True).replace(".", ""))
    installment_price = int(prices[2].get_text(strip=True).replace(".", ""))

    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

    return {
        "product_name": product_name,
        "old_price": old_price,
        "new_price": new_price,
        "installment_price": installment_price,
        "timestamp": timestamp,
    }


async def main():
    bot = TelegramBot(config.TOKEN, config.CHAT_ID)
    database = Database(config.DATABASE_URL)

    conn = database.create_connection()
    database.setup(conn)

    try:
        while True:
            page_content = fetch_page()
            product_info = parse_page(page_content)
            current_price = product_info["new_price"]

            max_price, max_price_timestamp = database.get_max_price(conn)

            if max_price is None or current_price > max_price:
                message = f"Novo preço maior detectado: {current_price}"
                print(message)
                await bot.send_message(message)
                max_price = current_price
                max_price_timestamp = product_info["timestamp"]
            else:
                message = f"O maior preço registrado é {max_price} em {max_price_timestamp}"
                print(message)
                await bot.send_message(message)

            database.save(product_info)
            print("Dados salvos no banco:", product_info)

            await asyncio.sleep(10)

    except KeyboardInterrupt:
        print("Parando a execução...")
    finally:
        conn.close()


asyncio.run(main())
