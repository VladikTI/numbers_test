from flask import Flask, render_template
import psycopg2
from main import get_sheets, put_in_database, watch_changes

app = Flask(__name__)


@app.route('/')
def index():
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
    return render_template('table.html', title='Supplies table',
                           orders=orders)


if __name__ == '__main__':
    orders = get_sheets()
    put_in_database(orders)
    app.run()
    exec(open('bot.py').read())
    watch_changes(orders)
