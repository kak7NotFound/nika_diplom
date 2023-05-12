import sqlite3

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

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
        [InlineKeyboardButton('Profile', callback_data='profile'),
         InlineKeyboardButton('Schedule', callback_data='schedule'),
         InlineKeyboardButton('News', callback_data='news')],
        [InlineKeyboardButton('Messages', callback_data='messages'),
         InlineKeyboardButton('Journals', callback_data='journals')]
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
async def callback_handler(bot, message):
    print(message)
    data = message.data
    print(data)
    await button_press(text=data, chat=message.message.chat)
    # Handle category selection
    if data.startswith('category:'):
        category_id = int(data.split(':')[1])
        subscribers_in_category = get_subscribers_in_category(category_id)
        text = 'Подписаны на категорию:\n' + '\n'.join(subscribers_in_category)
        await bot.send_message(chat_id=message.message.chat.id, text=text)

    # Handle main menu button press
    elif data == 'main_menu':
        text = 'Выберите категорию:'
        categories_keyboard = get_categories_keyboard()
        await bot.send_message(chat_id=message.message.chat.id, text=text, reply_markup=categories_keyboard)


async def button_press(text, chat):
    print(text)

    # Handle profile button press
    if text == 'profile':
        # Get the current message
        message = await bot.get_message(chat.id, chat.message_id)

        # Modify the message
        message.text = 'Ваш профиль'

        # Edit the message
        await bot.edit_message(chat.id, chat.message_id, message)

    # Handle schedule button press
    elif text == 'schedule':
        # Get the current message
        message = await bot.get_message(chat.id, chat.message_id)

        # Modify the message
        message.text = 'Ваш график'

        # Edit the message
        await bot.edit_message(chat.id, chat.message_id, message)

    # Handle news button press
    elif text == 'news':
        # Get the current message
        message = await bot.get_message(chat.id, chat.message_id)

        # Modify the message
        message.text = 'Последние новости'

        # Edit the message
        await bot.edit_message(chat.id, chat.message_id, message)

    # Handle messages button press
    elif text == 'messages':
        # Get the current message
        message = await bot.get_message(chat.id, chat.message_id)

        # Modify the message
        message.text = 'Ваши сообщения'

        # Edit the message
        await bot.edit_message(chat.id, chat.message_id, message)

    # Handle journals button press
    elif text == 'journals':
        # Get the current message
        message = await bot.get_message(chat.id, chat.message_id)

        # Modify the message
        message.text = 'Ваши журналы'

        # Edit the message
        await bot.edit_message(chat.id, chat.message_id, message)



bot.run()
