import sqlite3

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# Установка параметров подключения к Telegram API
api_id = '1590144'
api_hash = '4b90d9a931980a373d80a8d2828b158d'
bot_token = '1397501205:AAGm4tFnhcKwlbA3l6FkSBgHv8fB3MYW1PY'

# Инициализация клиента Telegram API
bot = Client('my_bot', api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# Установка параметров подключения к БД
db_filename = 'subscriptions.sqlite'

# Создание таблицы подписчиков
conn = sqlite3.connect(db_filename)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS subscribers (user_id INTEGER PRIMARY KEY)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS categories (category_name TEXT PRIMARY KEY)''')
conn.commit()


# Функция для получения списка подписчиков
def get_subscribers():
    cursor.execute('''SELECT user_id FROM subscribers''')
    rows = cursor.fetchall()
    return [row[0] for row in rows]


# Функция для получения списка подписчиков в категории
def get_subscribers_in_category(category_name):
    cursor.execute('''SELECT user_id FROM subscriptions WHERE category_name=?''', (category_name,))
    rows = cursor.fetchall()
    return [row[0] for row in rows]


# Функция для получения клавиатуры с кнопками категорий
def get_categories_keyboard():
    categories = get_categories()
    keyboard = []
    for category in categories:
        button = InlineKeyboardButton(category, callback_data=f'category_{category}')
        keyboard.append([button])
    return InlineKeyboardMarkup(keyboard)


# Функция для получения списка категорий
def get_categories():
    cursor.execute('''SELECT category_name FROM categories''')
    rows = cursor.fetchall()
    return [row[0] for row in rows]


# Функция для добавления подписчика
def add_subscriber(user_id):
    cursor.execute('''INSERT OR IGNORE INTO subscribers (user_id) VALUES (?)''', (user_id,))
    conn.commit()


# Функция для удаления подписчика
def remove_subscriber(user_id):
    cursor.execute('''DELETE FROM subscribers WHERE user_id=?''', (user_id,))
    conn.commit()


# Функция для добавления категории
def add_category(category_name):
    cursor.execute('''INSERT OR IGNORE INTO categories (category_name) VALUES (?)''', (category_name,))
    conn.commit()


# Функция для подписки на категорию
def subscribe(user_id, category_name):
    cursor.execute('''INSERT OR IGNORE INTO subscriptions (user_id, category_name) VALUES (?, ?)''',
                   (user_id, category_name))
    conn.commit()


# Функция для отписки от категории
def unsubscribe(user_id, category_name):
    cursor.execute('''DELETE FROM subscriptions WHERE user_id=? AND category_name=?''', (user_id, category_name))
    conn.commit()


# Обработчик команды /start
@bot.on_message(filters.command('start'))
async def start(bot, message):
    add_subscriber(message.chat.id)
    text = 'Добро пожаловать в информационную рассылку студентам абитуриентам!'

    # Отправляем главное меню с кнопками категорий
    categories_keyboard = get_categories_keyboard()
    await bot.send_message(chat_id=message.chat.id, text=text, reply_markup=categories_keyboard)


@bot.on_message(filters.command('help'))
async def help(bot, message):
    text = 'Список доступных команд: /start, /help, /unsubscribe'
    await bot.send_message(chat_id=message.chat.id, text=text)


@bot.on_message(filters.command('unsubscribe'))
async def unsubscribe(bot, message):
    user_id = message.chat.id
    remove_subscriber(user_id)
    text = 'Вы успешно отписались от рассылки'
    await bot.send_message(chat_id=message.chat.id, text=text)


@bot.on_callback_query()
async def callback_handler(bot, update):
    query = update.callback_query
    data = query.data
    print(data)
    # Обработка выбора категории
    if data.startswith('category:'):
        category_id = int(data.split(':')[1])
        subscribers_in_category = get_subscribers_in_category(category_id)
        text = 'Подписаны на категорию:\n' + '\n'.join(subscribers_in_category)
        await bot.send_message(chat_id=query.message.chat.id, text=text)

    # Обработка нажатия кнопки главного меню
    elif data == 'main_menu':
        text = 'Выберите категорию:'
        categories_keyboard = get_categories_keyboard()
        await bot.send_message(chat_id=query.message.chat.id, text=text, reply_markup=categories_keyboard)


bot.run()