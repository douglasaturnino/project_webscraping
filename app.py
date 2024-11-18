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


async def check_prices(context: ContextTypes.DEFAULT_TYPE):
    database = Database(config.DATABASE_URL)
    scraper = Scraper(context.job.data)

    conn = database.create_connection()

    try:
        page_content = scraper.fetch_page()
        product_info = scraper.parse_page(page_content)
        current_price = product_info["new_price"]

        min_price, min_price_timestamp = database.get_min_price(conn)

        if min_price is None or min_price > current_price:
            message = f"Menor preço encontrado: {current_price}"
            await context.bot.send_message(
                chat_id=context.job.chat_id, text=message
            )

        database.save(product_info)
        logger.info("Dados salvos no banco:", product_info)

    except Exception as e:
        print(f"Erro: {e}")
        await context.bot.send_message(
            chat_id=context.job.chat_id,
            text="Ocorreu um erro ao processar a verificação de preços. O trabalho será cancelado.",
        )  # Cancela o trabalho em caso de erro
        current_job = context.job
        current_job.schedule_removal()
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


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text.replace("/cancel", "").strip()
    if (
        "active_jobs" in context.chat_data
        and text in context.chat_data["active_jobs"]
    ):
        job_name = context.chat_data["active_jobs"][text]
        job = context.job_queue.get_jobs_by_name(job_name)

        if job:
            job[0].schedule_removal()
            await update.message.reply_text(
                "Verificação de preços para o link foi cancelada."
            )
            del context.chat_data["active_jobs"][text]

            database = Database(config.DATABASE_URL)
            conn = database.create_connection()
            database.delete_link(conn, text)
            conn.close()
        else:
            await update.message.reply_text(
                f"Não foi encontrada verificação de preços ativa para o link '{text}'."
            )
    else:
        await check(update, context)


async def get_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.replace("/link", "").strip()
    job_name = f"check_prices_{text}"

    if "active_jobs" not in context.chat_data:
        context.chat_data["active_jobs"] = {}

    context.chat_data["active_jobs"][text] = job_name

    database = Database(config.DATABASE_URL)
    conn = database.create_connection()
    database.save_link(conn, text, update.message.chat_id)
    conn.close()

    context.job_queue.run_repeating(
        check_prices,
        interval=60,
        first=10,
        data=text,
        chat_id=update.message.chat_id,
        name=job_name,
    )

    await update.message.reply_text("Verificação de preços iniciada.")


async def check(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if "active_jobs" in context.chat_data and context.chat_data["active_jobs"]:
        active_links = "\n".join(context.chat_data["active_jobs"].keys())
        await update.message.reply_text(
            f"Links sendo monitorados:\n{active_links}"
        )
    else:
        await update.message.reply_text(
            "Nenhum link está sendo monitorado no momento."
        )


def main() -> None:
    """Start the bot."""
    application = Application.builder().token(config.TOKEN).build()

    # Load links from database and add them to job queue
    database = Database(config.DATABASE_URL)
    conn = database.create_connection()
    active_links = database.get_links(conn)
    conn.close()

    for link, chat_id in active_links.items():
        job_name = f"check_prices_{link}"
        application.job_queue.run_repeating(
            check_prices,
            interval=60,
            first=10,
            data=link,
            chat_id=chat_id,
            name=job_name,
        )
        if "active_jobs" not in application.chat_data[chat_id]:
            application.chat_data[chat_id]["active_jobs"] = {}
        application.chat_data[chat_id]["active_jobs"][link] = job_name
        print(
            f"Link {link} adicionado ao job queue e context.chat_data para chat_id {chat_id}"
        )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("link", get_link))
    application.add_handler(CommandHandler("cancel", cancel))
    application.add_handler(CommandHandler("check", check))

    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, echo)
    )

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
