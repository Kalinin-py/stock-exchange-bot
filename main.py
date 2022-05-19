import telebot
import config
from telebot import types
from yahooticket import Ticker
import sqlite3

# from prettytable import from_db_cursor


# токен бота
BOT_TOKEN = config.TOKEN

bot = telebot.TeleBot(BOT_TOKEN)

btns_sample = ['AAPL', 'TSLA', 'FB', 'BTC-USD']


# создаем БД
def createDB():
    conn = sqlite3.connect('telega.db')
    cur = conn.cursor()
    # создаем таблицу users
    cur.execute('''CREATE TABLE IF NOT EXISTS users
                    (chatid INT PRIMARY KEY);''')

    # создаем таблицу tickets
    cur.execute('''CREATE TABLE IF NOT EXISTS tickets
                        (fkchatid INT,
                        ticket TEXT,
                        PRIMARY KEY(fkchatid, ticket));''')
    # сохраняем изменения в БД
    conn.commit()
    conn.close()


# создаем таблицу клиентов бота
def usersIns(usrID):
    try:
        conn = sqlite3.connect('telega.db')
        cur = conn.cursor()
        cur.execute(f'INSERT INTO users(chatid) VALUES({usrID})')
        conn.commit()
        conn.close()
    except:
        print('пользователь с таким ID зарегистрирован ранее')
    else:
        print('пользователь зарегистрирован в базе данных')


# наполняем таблицу Тикетс данными
def ticketIns(id, ticketName):
    conn = sqlite3.connect('telega.db')
    cur = conn.cursor()
    cur.execute(f'''INSERT OR IGNORE INTO tickets(fkchatid, ticket) VALUES({id}, '{ticketName}')''')
    conn.commit()
    conn.close()


# наполняем таблицу Тикетс данными
def getTable(id):
    conn = sqlite3.connect('telega.db')
    cur = conn.cursor()
    cur.execute(f'''SELECT ticket FROM tickets WHERE fkchatid = {id}''')
    tick = []
    for row in cur:
        tick.append(row[0])
    conn.close()
    return tick


# удаляем кнопки
def deleteBtn(btnName, id):
    conn = sqlite3.connect('telega.db')
    cur = conn.cursor()
    cur.execute(f'''delete from tickets where ticket = '{btnName}' and fkchatid = {id}''')
    conn.commit()
    conn.close()


# создаем клаву из списка
def createKb(btns2):
    itemAdd = types.KeyboardButton('Add')
    itemDel = types.KeyboardButton('Del')

    # добавляем кнопки
    markup = types.ReplyKeyboardMarkup()
    for b in btns2:
        markup.add(types.KeyboardButton(b))

    markup.row(itemAdd, itemDel)
    # возвращаем клаву
    return markup


'''
    создаем кнопки в Телеграм
'''


@bot.message_handler(commands=['start'])
def send_welcome(message):
    # сохраняем инф о пользователе
    usersIns(message.chat.id)
    # запрос к бд за инф
    btns2 = getTable(message.chat.id)
    klava = createKb(btns2)

    bot.send_message(message.chat.id, "Выберите акцию:", reply_markup=klava)


# отслеживаем все текстовые сообщения
@bot.message_handler(func=lambda message: True)
def echo_message(message):
    btns2 = getTable(message.from_user.id)
    if message.text == 'Del':
        if len(btns2) > 0:
            kb = types.InlineKeyboardMarkup()
            # циклом по списку
            for tick in btns2:
                kb.add(types.InlineKeyboardButton(tick, callback_data=tick + 'del'))

            bot.send_message(message.from_user.id, 'Укажите акцию для удаления:', reply_markup=kb)
    elif message.text == 'Add':
        if len(btns_sample) > 0:
            kb = types.InlineKeyboardMarkup()
            # циклом по списку
            for tick in btns_sample:
                kb.add(types.InlineKeyboardButton(tick, callback_data=tick + 'ins'))

            bot.send_message(message.from_user.id, 'Укажите акцию для отслеживания:', reply_markup=kb)
    else:
        if message.text in btns2:
            t = Ticker(message.text)
            t.update()
            bot.reply_to(message, f'Цена : {t.price} ({t.percent})')
        else:
            t = Ticker(message.text)
            if t.checkTicket():
                ticketIns(message.from_user.id, message.text.upper())
                btns2 = getTable(message.from_user.id)
                kb = createKb(btns2)
                bot.reply_to(message, f'Акция {message.text.upper()} добавлена', reply_markup=kb)


# обработка ответов с кнопок
@bot.callback_query_handler(func=lambda call: True)
def call_message(call):
    s = call.data

    # c помощью среза определяем требуемое действие и саму акцию
    if s[-3:] == 'del':
        # удаляем элемент из списка кнопок-акций
        deleteBtn(s[:-3], call.message.chat.id)
        # пересобираем клавиатуру из списка-акций
        btns2 = getTable(call.message.chat.id)
        kb = createKb(btns2)
        # удаляем текущую клаву
        # a = types.ReplyKeyboardRemove()
        bot.send_message(call.message.chat.id, f'{s[-3:]} удалена', reply_markup=kb)
    else:
        ticketIns(call.message.chat.id, s[:-3])
        btns2 = getTable(call.message.chat.id)
        # пересобираем клавиатуру из списка-акций
        kb = createKb(btns2)
        # удаляем текущую клаву
        # a = types.ReplyKeyboardRemove()
        bot.send_message(call.message.chat.id, f'{s[:-3]} добавлена', reply_markup=kb)
        # else:
        #     bot.send_message(call.message.chat.id, f'{s[:-3]} добавлена была ранее')


# создаем БД
createDB()

bot.infinity_polling()
