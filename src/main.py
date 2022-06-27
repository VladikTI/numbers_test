import psycopg2
import xml.etree.ElementTree as ET
import httplib2
import apiclient
import requests
from oauth2client.service_account import ServiceAccountCredentials
import time


def get_sheets():
    CREDENTIALS_FILE = 'creds.json' # путь к файлу с api токенами
    spreadsheet_id = '1uhirrVB73FENo6BIYd4f5oJDCxdtQcDeupesEz99jxA' # id google sheets файла

    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        CREDENTIALS_FILE,
        ['https://www.googleapis.com/auth/spreadsheets',
         'https://www.googleapis.com/auth/drive']) # указываем сервисы, с которыми будем работать
    http_auth = credentials.authorize(httplib2.Http()) # объект для работы с запросами
    service = apiclient.discovery.build('sheets', 'v4', http=http_auth) # экзмепляр api

    values = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range='A:Z',
        majorDimension='ROWS'
    ).execute() # получаем значения из таблицы, указывем google sheet id, диапазон поиска, вид представления данных

    return values['values'] # возвращаем список со строками таблицы


def put_in_database(orders):
    connection = psycopg2.connect(
        database="postgres",
        user="postgres",
        password="numbers",
        host="postgres_db",
        port="5432") # соединяемся с postgreSQL DB

    get_xml = requests.get('http://www.cbr.ru/scripts/XML_daily.asp') # отправляем запрос ЦБ РФ для получения курса валют
    structure = ET.fromstring(get_xml.content)
    dollar = structure.find("./*[@ID='R01235']/Value") # ищем по ID информацию о долларе
    dollar_exchange_rate = float(dollar.text.replace(',', '.'))
    overdue_deliveries = []
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS order_parameters (Order_Number Integer, "
                   "Price_RUB Integer, Price_USD Integer, Delivery_Term Text)") # если таблицы в DB нет - создаем
    cursor.execute("SELECT Order_Number, Price_RUB, Price_USD, Delivery_Term from order_parameters") # получаем строки таблицы
    rows = cursor.fetchall() # эти строки сохраняем в переменной
    for order in orders[1:]:
        price_rub = int(float(order[1]) * dollar_exchange_rate) # переводим цену в рубли
        mark = "'"
        if int(order[0]) <= len(rows): # если номер заказа меньше, чем кол-во строк DB, значит эти заказы уже в DB. Так что обновляем
            cursor.execute(f'UPDATE order_parameters set Price_USD = {order[1]} where Order_Number = {order[0]}')
            cursor.execute(f'UPDATE order_parameters set Price_RUB = {price_rub} where Order_Number = {order[0]}')
            cursor.execute(f'UPDATE order_parameters set Delivery_Term = {mark}{order[2]}{mark} where Order_Number = {order[0]}')
            continue
        cursor.execute(
            f'INSERT INTO order_parameters (Order_Number,Price_USD,Price_RUB,Delivery_Term) VALUES ({order[0]}, {price_rub}, {order[1]}, {mark}{order[2]}{mark})')
            # в противном случае просто добавляем новую строку в DB

    if len(orders[1:]) < len(rows): # если кол-во строк таблицы меньше, чем в DB, то нужно удалить лишние из DB
        for row in rows[len(orders[1:]):]:
            cursor.execute(f'DELETE from order_parameters where Order_Number={row[0]}')

    connection.commit()

    connection.close()


def watch_changes(orders):
    while True: # раз в 30 секунд проверяет на обновление данных в google sheets
        time.sleep(30)
        new_orders = get_sheets()
        if new_orders != orders:
            put_in_database(new_orders)
            orders = new_orders


if __name__ == "__main__":
    overdue_deliveries = []
    orders = get_sheets()
    put_in_database(orders)
    watch_changes(orders)