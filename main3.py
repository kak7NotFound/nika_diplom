import sqlite3

import pyrogram.types.user_and_chats
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import datetime

import requests
import json

# Set up Telegram API parameters
api_id = '1590144'
api_hash = '4b90d9a931980a373d80a8d2828b158d'
bot_token = '1397501205:AAGm4tFnhcKwlbA3l6FkSBgHv8fB3MYW1PY'

# Initialize Telegram API client
bot = Client('my_bot', api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# Set up database connection parameters
db_filename = 'subscriptions.sqlite'

# Create subscribers table
conn = sqlite3.connect(db_filename)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS subscribers (
    user_id INTEGER PRIMARY KEY
)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS categories (
    category_name TEXT PRIMARY KEY
)''')
conn.commit()


# Function to get list of subscribers
def get_subscribers():
    cursor.execute('''SELECT user_id FROM subscribers''')
    rows = cursor.fetchall()
    return [row[0] for row in rows]


# Function to get list of subscribers in category
def get_subscribers_in_category(category_name):
    cursor.execute('''SELECT user_id FROM subscriptions WHERE category_name=?''', (category_name,))
    rows = cursor.fetchall()
    return [row[0] for row in rows]


# Function to get keyboard with category buttons
def get_categories_keyboard():
    categories = get_categories()
    keyboard = []
    for category in categories:
        button = InlineKeyboardButton(category, callback_data=f'category_{category}')
        keyboard.append([button])
    return InlineKeyboardMarkup(keyboard)


# Function to get list of categories
def get_categories():
    cursor.execute('''SELECT category_name FROM categories''')
    rows = cursor.fetchall()
    return [row[0] for row in rows]


# Function to add subscriber
def add_subscriber(user_id):
    cursor.execute('''INSERT OR IGNORE INTO subscribers (user_id) VALUES (?)''', (user_id,))
    conn.commit()


# Function to remove subscriber
def remove_subscriber(user_id):
    cursor.execute('''DELETE FROM subscribers WHERE user_id=?''', (user_id,))
    conn.commit()


# Function to add category
def add_category(category_name):
    cursor.execute('''INSERT OR IGNORE INTO categories (category_name) VALUES (?)''', (category_name,))
    conn.commit()


# Function to subscribe to category
def subscribe(user_id, category_name):
    cursor.execute('''INSERT OR IGNORE INTO subscriptions (user_id, category_name) VALUES (?, ?)''',
                   (user_id, category_name))
    conn.commit()


# Function to unsubscribe from category
def unsubscribe(user_id, category_name):
    cursor.execute('''DELETE FROM subscriptions WHERE user_id=? AND category_name=?''', (user_id, category_name))
    conn.commit()


# Handler for /start command
@bot.on_message(filters.command('start'))
async def start(bot, message):
    add_subscriber(message.chat.id)
    text = 'Добро пожаловать в информационную рассылку!'

    # Send main menu with category buttons
    categories_keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton('Профиль', callback_data='profile'),
            InlineKeyboardButton('Расписание', callback_data='schedule'),
            InlineKeyboardButton('Новости', callback_data='news')
        ],
        [
            InlineKeyboardButton('Сообщения', callback_data='messages'),
            InlineKeyboardButton('Журналы', callback_data='journals')
        ]
    ])
    await bot.send_message(chat_id=message.chat.id, text=text, reply_markup=categories_keyboard)


# Handler for /help command
@bot.on_message(filters.command('help'))
async def help(bot, message):
    text = 'Список доступных команд: /start, /help, /unsubscribe'
    await bot.send_message(chat_id=message.chat.id, text=text)


# Handler for /unsubscribe command
@bot.on_message(filters.command('unsubscribe'))
async def unsubscribe(bot, message):
    user_id = message.chat.id
    remove_subscriber(user_id)
    text = 'Вы успешно отписались от рассылки'
    await bot.send_message(chat_id=message.chat.id, text=text)


# Handler for callback query
@bot.on_callback_query()
async def callback_handler(bot, event:pyrogram.types.bots_and_keyboards.callback_query.CallbackQuery):
    data = event.data
    await button_press(text=data, event=event)


async def button_press(text, event: pyrogram.types.bots_and_keyboards.callback_query.CallbackQuery):
    chat = event.message.chat
    print(text)
    if text == 'profile':
        await event.answer('Вы выбрали Профиль')
        await event.message.edit_text('Сообщение для Профиля')
        await event.message.edit_reply_markup(
            InlineKeyboardMarkup([[InlineKeyboardButton('Назад', callback_data='main_menu')]]))

    elif text == 'schedule':
        await event.answer('Вы выбрали Расписание')
        # Get the JSON data
        url = "https://edu-tpi.donstu.ru/api/Rasp?idGroup=2874"
        response = requests.get(url)
        data: dict = json.loads(response.content)

        rasp = []
        for d in data.get("data").get("rasp"):
        # МЕТОД ДЛЯ СЕГОДНЯ
        #     if datetime.datetime.now().isoformat()[0:10] == d.get("дата")[0:10]:
            if "2022-09-13" == d.get("дата")[0:10]:
                rasp.append(d)

        text = ""

        if len(rasp) == 0:
            text = "Расписание на сегодня: \n\nРасписание отсутствует"
        else:
            text = f"Расписание на сегодня\n\n"
            for i in rasp:
               text = text + \
                      f"Предмет: {i.get('дисциплина')}\n" \
                      f"Начало: {i.get('начало')}\n" \
                      f"Конец: {i.get('конец')}\n" \
                      f"Аудитория: {i.get('аудитория')}\n" \
                      f"Преподаватель: {i.get('преподаватель')}\n\n"

        await event.message.edit_text(text)

        await event.message.edit_reply_markup(
            InlineKeyboardMarkup([[InlineKeyboardButton('Назад', callback_data='main_menu')]]))


    elif text == 'news':
        await event.answer('Вы выбрали Новости')
        await event.message.edit_text('Сообщение для Новостей')
        await event.message.edit_reply_markup(
            InlineKeyboardMarkup([[InlineKeyboardButton('Назад', callback_data='main_menu')]]))
    elif text == 'messages':
        await event.answer('Вы выбрали Сообщения')
        await event.message.edit_text('Сообщение для Сообщений')
        await event.message.edit_reply_markup(
            InlineKeyboardMarkup([[InlineKeyboardButton('Назад', callback_data='main_menu')]]))
    elif text == 'journals':
        await event.answer('Вы выбрали Журналы')
        await event.message.edit_text('Сообщение для Журналов')
        await event.message.edit_reply_markup(
            InlineKeyboardMarkup([[InlineKeyboardButton('Назад', callback_data='main_menu')]]))
    elif text == 'main_menu':
        # Отправляем сообщение с главным меню
        categories_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton('Профиль', callback_data='profile'),
             InlineKeyboardButton('Расписание', callback_data='schedule'),
             InlineKeyboardButton('Новости', callback_data='news')],
            [InlineKeyboardButton('Сообщения', callback_data='messages'),
             InlineKeyboardButton('Журналы', callback_data='journals')]
        ])
        await event.message.edit_text('Выберите категорию:', reply_markup=categories_keyboard)
    else:
        await event.answer('Неизвестная кнопка')


bot.run()
