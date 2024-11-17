from telegram import Bot


class TelegramBot:
    def __init__(self, token: str, chat_id: str):
        self.bot = Bot(token=token)
        self.chat_id = chat_id

    async def send_message(self, text: str) -> None:
        await self.bot.send_message(chat_id=self.chat_id, text=text)
