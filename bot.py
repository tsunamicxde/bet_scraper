import logging
from aiogram import Bot, Dispatcher, executor, types

import config

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.bot_token)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Привет! Я бот для отправки уведомлений.")


async def send_notification(text: str):
    await bot.send_message(chat_id=config.chat_id, text=text)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
