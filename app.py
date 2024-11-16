import sqlite3
import time

import pandas as pd
import requests
from bs4 import BeautifulSoup


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


def create_connection(db_name="prices.db"):
    conn = sqlite3.connect(db_name)
    return conn


def setup_database(conn):
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT,
            old_price INTEGER,
            new_price INTEGER,
            installment_price INTEGER,
            timestamp TEXT
        )
    """)
    conn.commit()


def save_to_database(conn, data):
    df = pd.DataFrame([data])
    df.to_sql("prices", conn, if_exists="append", index=False)


def get_max_price(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(new_price), timestamp FROM prices")
    result = cursor.fetchone()
    if result and result[0] is not None:
        return result[0], result[1]
    return None, None


if __name__ == "__main__":
    conn = create_connection()
    setup_database(conn)

    while True:
        page_content = fetch_page()
        product_info = parse_page(page_content)
        current_price = product_info["new_price"]

        max_price, max_price_timestamp = get_max_price(conn)

        if max_price is None or current_price > max_price:
            print(f"Preço maior detectado: {current_price}")
            max_price = current_price
            max_price_timestamp = product_info["timestamp"]
        else:
            print(
                f"O maior preço registrado é {max_price} em {max_price_timestamp}"
            )

        save_to_database(conn, product_info)
        print("Dados salvos no banco:", product_info)

        time.sleep(10)

    conn.close()
