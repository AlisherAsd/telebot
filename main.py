import telebot
import webbrowser
from telebot import types
import sqlite3
import requests
import json



bot = telebot.TeleBot('6968992565:AAG9sRnudHNKaKBAilhoWlywjAYj-wfMZWM')
API ='fb7ac44a011097c96ec9a3773427ee56'

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton('/start')
    btn2 = types.KeyboardButton('/help')
    markup.row(btn1, btn2)
    bot.send_message(message.chat.id, f'Hello {message.from_user.first_name} {message.from_user.last_name}! Пропиши /help чтобы узнать команды.', reply_markup=markup)


@bot.message_handler(commands=['help'])
def info(message):
    bot.send_message(message.chat.id, '<b>Help Command</b> \n\n  /website - сайт нашего проекта \n\n /kick - исключить участника группы \n\n /dis - сборник задач по дискретке \n\n /mat - сборник задач по матанализу \n\n /register - регистрация пользователя \n\n /help - выводит команды \n\n /users - список пользователей \n\n /weather - узнать температуру в вашем городе', parse_mode='html')


# Регистрация пользователя

name = None

@bot.message_handler(commands=['register'])
def register(message):
    connect = sqlite3.connect('user.sql')
    cursor = connect.cursor()

    cursor.execute('CREATE TABLE IF NOT EXISTS user (id int auto_increment primary key, name varchar(50), pass varchar(50))')
    connect.commit()
    cursor.close()
    connect.close()

    bot.send_message(message.chat.id, 'Введите имя для регистрации.')
    bot.register_next_step_handler(message, user_name)

def user_name(message):
    global name
    name = message.text.strip()
    bot.send_message(message.chat.id, 'Введите пароль.')
    bot.register_next_step_handler(message, user_pass)

def user_pass(message):
    password = message.text.strip()

    connect = sqlite3.connect('user.sql')
    cursor = connect.cursor()

    cursor.execute("INSERT INTO user (name, pass) VALUES ('%s', '%s')" % (name, password))

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Список пользователей', callback_data='users'))
    bot.send_message(message.chat.id, 'Пользователь зарегистрирован!', reply_markup=markup)

    connect.commit()
    cursor.close()
    connect.close()

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    connect = sqlite3.connect('user.sql')
    cursor = connect.cursor()

    cursor.execute('SELECT * FROM user')
    users = cursor.fetchall()

    info = ''
    for el in users:
        info += f'Имя - {el[1]}, Пароль - {el[2]}\n'

    cursor.close()
    connect.close()

    bot.send_message(call.message.chat.id, info)


@bot.message_handler(commands=['users'])
def users(message):
    connect = sqlite3.connect('user.sql')
    cursor = connect.cursor()

    cursor.execute('SELECT * FROM user')
    users = cursor.fetchall()

    info = ''
    for el in users:
        info += f'Имя - {el[1]}, Пароль - {el[2]}\n'

    cursor.close()
    connect.close()

    bot.send_message(message.chat.id, info)

@bot.message_handler(content_types=['photo'])
def get_photo(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Удалить фото', callback_data = 'delete'))
    bot.reply_to(message, 'Иконка вашего профиля!', reply_markup = markup)


# ---------------------------------------------------------------


@bot.message_handler(commands=['website'])
def info(message):
    webbrowser.open('https://ya.ru/')

@bot.message_handler(commands=['dis'])
def dis(message):
    file = open('dop/diskretka.pdf', 'rb')
    bot.send_document(message.chat.id, file)

@bot.message_handler(commands=['mat'])
def mat(message):
    file = open('dop/matanal.pdf', 'rb')
    bot.send_document(message.chat.id, file)



# Исключение участника беседы
@bot.message_handler(commands=['kick'])
def kick_user(message):
    if message.reply_to_message:
        chat_id = message.chat.id
        user_id = message.reply_to_message.from_user.id
        user_status = bot.get_chat_member(chat_id, user_id).status
        if user_status == 'administrator' or user_status == 'creator':
            bot.reply_to(message, "Невозможно исключить администратора.")
        else:
            bot.kick_chat_member(chat_id, user_id)
            bot.reply_to(message, f"Пользователь {message.reply_to_message.from_user.username} был исключен.")
    else:
        bot.reply_to(message, "Эта команда должна быть использована в ответ на сообщение участника, которого вы хотите исключить")

@bot.callback_query_handler(func=lambda callback: True)
def call_message(callback):
    if callback.data == 'delete':
        bot.delete_message(callback.message.chat.id, callback.message.message_id - 1)

# Выдача температуры в городе
@bot.message_handler(commands=['weather'])
def weather(message):
    bot.send_message(message.chat.id, 'Чтобы узнать погоду, введите ваш город.')

@bot.message_handler(content_types=['text'])
def get_weather(message):
    city = message.text.strip().lower()
    res = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API}&units=metric')
    data = json.loads(res.text)
    bot.reply_to(message, f'Температура: {data["main"]["temp"]}°')





bot.polling(none_stop= True)


