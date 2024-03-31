import logging
import re
import sqlite3
import os

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from automation.draw_graphs import draw_graphs

from automation.write_to_file import write_to_file


import config

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.bot_token)
dp = Dispatcher(bot)
storage = MemoryStorage()

conn = sqlite3.connect('matches_data.db')
cursor = conn.cursor()

cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER UNIQUE
                    )
                ''')
conn.commit()


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    user_id = message.from_user.id

    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    existing_user = cursor.fetchone()
    if not existing_user:
        cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
        conn.commit()
        await message.reply("📊 Приветствую вас! Я ваш надежный помощник для отслеживания изменений коэффициентов.\n"
                            "📈 Здесь вы будете получать своевременные уведомления о любых изменениях "
                            "в коэффициентах матчей таких игр, как:\n"
                            "DOTA 2, CS 2, League Of Legends, Mobile Legends.")
    else:
        await message.reply("С возвращением! Я готов к отправке уведомлений.")


async def send_notification(text: str, left_team_name: str, right_team_name: str):
    cursor.execute("SELECT user_id FROM users")
    user_ids = cursor.fetchall()

    for user_id in user_ids:
        markup = types.InlineKeyboardMarkup(row_width=1)
        watch_graphs_button = types.InlineKeyboardButton("Посмотреть графики 📈",
                                                         callback_data=f"{left_team_name}_{right_team_name}")
        markup.add(watch_graphs_button)

        await bot.send_message(chat_id=user_id[0], text=text, reply_markup=markup)


@dp.callback_query_handler(lambda callback_query: True)
async def callback(call):
    user_id = call.message.chat.id
    call_data = call.data
    write_to_file(config.file_name, call_data)
    if re.match(r'^[a-zA-Z0-9_ ]+[_][a-zA-Z0-9_ ]+$', call_data):
        teams = call_data.split('_')
        draw_graphs(teams[0], teams[1])

        directory = 'graphics/'
        for filename in os.listdir(directory):
            if filename.endswith('.png') and call_data in filename:
                file_path = os.path.join(directory, filename)
                with open(file_path, 'rb') as file:
                    await bot.send_photo(user_id, file)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
