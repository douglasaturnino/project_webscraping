import asyncio

from config import Config as config
from database import Database
from scraper import Scraper
from telegram_bot import TelegramBot


async def main():
    bot = TelegramBot(config.TOKEN, config.CHAT_ID)
    database = Database(config.DATABASE_URL)
    scraper = Scraper()

    conn = database.create_connection()
    database.setup(conn)

    try:
        while True:
            page_content = scraper.fetch_page()
            product_info = scraper.parse_page(page_content)
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
