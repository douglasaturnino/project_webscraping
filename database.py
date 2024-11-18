from typing import Any, Dict, Tuple

import pandas as pd
import psycopg2
from sqlalchemy import create_engine

from config import Config as config


class Database:
    def __init__(self, url: str):
        self.engine = create_engine(url)

    def create_connection(self):
        return psycopg2.connect(
            dbname=config.POSTGRES_DB,
            user=config.POSTGRES_USER,
            password=config.POSTGRES_PASSWORD,
            host=config.POSTGRES_HOST,
            port=config.POSTGRES_PORT,
        )

    def setup(self, conn) -> None:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS prices (
            id SERIAL PRIMARY KEY,
            product_name TEXT,
            old_price INTEGER,
            new_price INTEGER,
            installment_price INTEGER,
            timestamp TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS links (
            id SERIAL PRIMARY KEY,
            link TEXT UNIQUE,
            chat_id BIGINT
        );
    """)
        conn.commit()
        cursor.close()

    def save(self, data: Dict[str, Any], table_name="prices") -> None:
        df = pd.DataFrame([data])
        df.to_sql(table_name, self.engine, if_exists="append", index=False)

    def get_max_price(self, conn) -> Tuple[int, str]:
        cursor = conn.cursor()
        cursor.execute(
            """ SELECT new_price, timestamp FROM prices WHERE new_price = (SELECT MAX(new_price) FROM prices); """
        )
        result = cursor.fetchone()
        cursor.close()
        if result and result[0] is not None:
            return result[0], result[1]
        return None, None

    def save_link(self, conn, link: str, chat_id: int) -> None:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO links (link, chat_id) VALUES (%s, %s)
            ON CONFLICT (link) DO NOTHING;
        """,
            (link, chat_id),
        )
        conn.commit()
        cursor.close()

    def delete_link(self, conn, link: str) -> None:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM links WHERE link = %s;", (link,))
        conn.commit()
        cursor.close()

    def get_links(self, conn) -> Dict[str, int]:
        cursor = conn.cursor()
        cursor.execute("SELECT link, chat_id FROM links;")
        links = cursor.fetchall()
        cursor.close()
        return {link: chat_id for link, chat_id in links}
