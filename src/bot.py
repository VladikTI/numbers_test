import psycopg2
import telebot
from telebot import types
from datetime import date
import datetime

bot = telebot.TeleBot('5306045060:AAHwXgD-2udLEiDyzpBtGC-jwYZw_YAwszM')


def connect_db():
    overdue_deliveries = []
    connection = psycopg2.connect(
        database="postgres",
        user="postgres",
        password="numbers",
        host="postgres_db",
        port="5432") # подключаемся к postgreSQL DB
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS order_parameters (Order_Number Integer, "
                   "Price_RUB Integer, Price_USD Integer, Delivery_Term Text)") # если таблицы в DB нет - создаем
    cursor.execute("SELECT Order_Number, Price_RUB, Price_USD, Delivery_Term from order_parameters") # получаем строки таблицы
    orders = cursor.fetchall() # эти строки сохраняем в переменной
    for order in orders:
        if datetime.date.today() > date(int(order[3].split('.')[2]), int(order[3].split('.')[1]), int(order[3].split('.')[0])): # сравниваем сегодняшнюю дату и дату поставки; если просрочено, добавляем в список
            overdue_deliveries.append(order)
    return overdue_deliveries


@bot.message_handler(commands=["start"]) # скрипт ждет команду /start
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True) # создаем табло для вариантов ответ
    item = types.KeyboardButton('Получить информацию о просроченных поставках') # создаем кнопку с текстом
    markup.add(item) # добавляем кнопку в табло
    bot.send_message(message.chat.id, 'Нажми на кнопку для получения информации о поставках.', reply_markup=markup) # отвечаем пользователю, вариант ответа: наша кнопка


@bot.message_handler(content_types=["text"]) # скрипт ждет сообщение от пользователя
def handle_text(message):
    if message.text.strip() == 'Получить информацию о просроченных поставках': # если текст сообщения равен тексту кнопки
        overdue_deliveries = connect_db()
        connect_db()
        if not overdue_deliveries:
            bot.send_message(message.chat.id, 'Информация отсутствует')
        else:
            answer = 'Просроченные поставки\n'
            for parameter in overdue_deliveries:
                answer += f'Поставка №{parameter[0]}: Цена,руб - {parameter[1]}; Цена,usd - {parameter[2]}; Срок поставки - {parameter[3]}.\n'
            bot.send_message(message.chat.id, answer)


bot.polling(none_stop=True, interval=0)
