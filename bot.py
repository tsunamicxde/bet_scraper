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

storage = MemoryStorage()
bot = Bot(token=config.bot_token)
dp = Dispatcher(bot, storage=storage)

conn = sqlite3.connect('matches_data.db')
cursor = conn.cursor()

cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER UNIQUE
                    )
                ''')
conn.commit()


all_games = ['DOTA 2', 'CS 2', 'League Of Legends', 'Mobile Legends']


def call_menu():
    markup = types.InlineKeyboardMarkup(row_width=1)
    head_button = types.InlineKeyboardButton("Вернуться к матчам 🏀", callback_data="head")
    cancel_button = types.InlineKeyboardButton("Отмена 🔙", callback_data="cancel")
    markup.add(head_button, cancel_button)
    return markup


def game_selection():
    markup = types.InlineKeyboardMarkup(row_width=1)
    dota_button = types.InlineKeyboardButton("DOTA 2", callback_data="DOTA 2")
    cs_button = types.InlineKeyboardButton("CS 2", callback_data="CS 2")
    lol_button = types.InlineKeyboardButton("League Of Legends", callback_data="League Of Legends")
    ml_button = types.InlineKeyboardButton("Mobile Legends", callback_data="Mobile Legends")
    markup.add(dota_button, cs_button, lol_button, ml_button)
    return markup


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    user_id = message.from_user.id

    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    existing_user = cursor.fetchone()

    markup = types.InlineKeyboardMarkup(row_width=1)
    matches_info_button = types.InlineKeyboardButton("Посмотреть информацию о матчах 🏀",
                                                     callback_data="matches-info")
    markup.add(matches_info_button)

    await message.reply("📊 Приветствую вас! Я ваш надежный помощник для отслеживания изменений коэффициентов.\n\n"
                        "📈 Здесь вы будете получать своевременные уведомления о любых изменениях "
                        "в коэффициентах матчей таких игр, как:\n"
                        "DOTA 2, CS 2, League Of Legends, Mobile Legends.\n\n"
                        "Также вы можете посмотреть информацию о любом интересующем вас матче", reply_markup=markup)

    if not existing_user:
        cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
        conn.commit()


async def send_notification(text: str, type_of_coefficient: str, match_id: int):
    cursor.execute("SELECT user_id FROM users")
    user_ids = cursor.fetchall()

    for user_id in user_ids:
        markup = types.InlineKeyboardMarkup(row_width=1)
        watch_graphs_button = types.InlineKeyboardButton("Посмотреть график 📈",
                                                         callback_data=f"{match_id}_{type_of_coefficient}")
        markup.add(watch_graphs_button)

        await bot.send_message(chat_id=user_id[0], text=text, reply_markup=markup)


@dp.callback_query_handler(lambda callback_query: True)
async def callback(call, state: FSMContext):
    user_id = call.message.chat.id
    call_data = call.data
    write_to_file(config.file_name, call_data)

    if re.match(r'^[0-9]+[_][a-zA-Z0-9.]+$', call_data):
        teams = call_data.split('_')

        draw_graphs(teams[0], [teams[1]])

        is_none = False

        if teams[1] == "None":
            is_none = True

        directory = 'graphics/'
        for filename in os.listdir(directory):
            if filename.endswith('.png') and f"{teams[0]}" in filename:
                if not is_none:
                    if teams[1] in filename:
                        file_path = os.path.join(directory, filename)
                        with open(file_path, 'rb') as file:
                            markup = types.InlineKeyboardMarkup(row_width=1)
                            delete_graphics_button = types.InlineKeyboardButton("Удалить график ❌",
                                                                                callback_data=f"delete-{call_data}")
                            markup.add(delete_graphics_button)

                            await bot.send_photo(user_id, file, reply_markup=markup)

                else:
                    file_path = os.path.join(directory, filename)
                    with open(file_path, 'rb') as file:
                        markup = types.InlineKeyboardMarkup(row_width=1)
                        delete_graphics_button = types.InlineKeyboardButton("Удалить график ❌",
                                                                            callback_data=f"delete-{call_data}")
                        markup.add(delete_graphics_button)

                        await bot.send_photo(user_id, file, reply_markup=markup)

        keyboard = call_menu()
        await bot.send_message(user_id, "Выберите опцию:", reply_markup=keyboard)

    elif call_data == "matches-info":
        try:
            keyboard = game_selection()
            await bot.send_message(user_id, "Выберите игру 🎮", reply_markup=keyboard)
        except Exception as ex:
            write_to_file(config.file_name, ex)

    elif call_data in all_games:
        async with state.proxy() as data:
            data['game'] = call_data
            write_to_file(config.file_name, data['game'])

        cursor.execute(f"SELECT DISTINCT league_name FROM matches_data WHERE game = ?", (call_data, ))

        unique_league_names = cursor.fetchall()

        markup = types.InlineKeyboardMarkup(row_width=1)
        for league_name in unique_league_names:
            league_button = types.InlineKeyboardButton(league_name[0],
                                                       callback_data=f"L:{league_name[0]}")
            markup.add(league_button)

        await bot.send_message(user_id, "Выберите лигу 🏆", reply_markup=markup)

    elif call_data.startswith("L:"):
        league_name = call_data[2:]

        async with state.proxy() as data:
            game = data['game']
            write_to_file(config.file_name, data['game'])

        sql_query = f"""SELECT match_id, left_team_name, right_team_name
                       FROM matches_data
                       WHERE league_name = ? AND game = ?"""

        cursor.execute(sql_query, (league_name, game))

        teams = cursor.fetchall()

        markup = types.InlineKeyboardMarkup(row_width=1)

        for match_id, left_team, right_team in teams:
            match_button = types.InlineKeyboardButton(f"{left_team} vs {right_team}",
                                                      callback_data=f"{match_id}_None")
            markup.add(match_button)

        await bot.send_message(user_id, "Выберите матч 🏀", reply_markup=markup)

    elif call_data == "head":
        markup = types.InlineKeyboardMarkup(row_width=1)
        matches_info_button = types.InlineKeyboardButton("Посмотреть информацию о матчах 🏀",
                                                         callback_data="matches-info")
        markup.add(matches_info_button)

        await bot.send_message(user_id, "Здесь вы можете посмотреть список всех матчей: ", reply_markup=markup)

    elif call_data.startswith("delete-"):
        message_id = call.message.message_id

        await bot.delete_message(chat_id=call.message.chat.id, message_id=message_id)

        await bot.answer_callback_query(call.id, text="График удален ✅")

    elif call_data == "cancel":
        await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
