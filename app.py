import asyncio
import time

import pandas as pd
import psycopg2
import requests
from bs4 import BeautifulSoup
from sqlalchemy import create_engine
from telegram import Bot

from config import Config as config

bot = Bot(token=config.TOKEN)


engine = create_engine(config.DATABASE_URL)


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


def create_connection():
    conn = psycopg2.connect(
        dbname=config.POSTGRES_DB,
        user=config.POSTGRES_USER,
        password=config.POSTGRES_PASSWORD,
        host=config.POSTGRES_HOST,
        port=config.POSTGRES_PORT,
    )
    return conn


def setup_database(conn):
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS prices (
            id SERIAL PRIMARY KEY,
            product_name TEXT,
            old_price INTEGER,
            new_price INTEGER,
            installment_price INTEGER,
            timestamp TIMESTAMP
        )
    """)
    conn.commit()
    cursor.close()


def save_to_database(data, table_name="prices"):
    df = pd.DataFrame([data])
    df.to_sql(table_name, engine, if_exists="append", index=False)


def get_max_price(conn):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT new_price, timestamp 
        FROM prices 
        WHERE new_price = (SELECT MAX(new_price) FROM prices);
    """)
    result = cursor.fetchone()
    cursor.close()
    if result and result[0] is not None:
        return result[0], result[1]
    return None, None


async def send_telegram_message(text):
    await bot.send_message(chat_id=config.CHAT_ID, text=text)


async def main():
    conn = create_connection()
    setup_database(conn)

    try:
        while True:
            page_content = fetch_page()
            product_info = parse_page(page_content)
            current_price = product_info["new_price"]

            max_price, max_price_timestamp = get_max_price(conn)

            if max_price is None or current_price > max_price:
                message = f"Novo preço maior detectado: {current_price}"
                print(message)
                await send_telegram_message(message)
                max_price = current_price
                max_price_timestamp = product_info["timestamp"]
            else:
                message = f"O maior preço registrado é {max_price} em {max_price_timestamp}"
                print(message)
                await send_telegram_message(message)

            save_to_database(product_info)
            print("Dados salvos no banco:", product_info)

            await asyncio.sleep(10)

    except KeyboardInterrupt:
        print("Parando a execução...")
    finally:
        conn.close()


asyncio.run(main())
