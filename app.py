import asyncio
import logging

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from config import Config as config
from database import Database
from scraper import Scraper


async def main2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    database = Database(config.DATABASE_URL)
    text = update.message.text.replace("/link", "").strip()
    scraper = Scraper(text)

    conn = database.create_connection()
    database.setup(conn)

    try:
        while True:
            page_content = scraper.fetch_page()
            product_info = scraper.parse_page(page_content)
            current_price = product_info["new_price"]

            min_price, min_price_timestamp = database.get_min_price(conn)

            if min_price is None or min_price > current_price:
                message = f"Novo preço maior detectado: {current_price}"
                print(message)
                await context.send_message(message)

            database.save(product_info)
            print("Dados salvos no banco:", product_info)

            await asyncio.sleep(60)

    except KeyboardInterrupt:
        print("Parando a execução...")
    finally:
        conn.close()


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.first_name}!",
    )


async def help_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    await update.message.reply_text("Help!")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(update.message.text)


def main() -> None:
    application = Application.builder().token(config.TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("link", main2))

    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, echo)
    )

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
