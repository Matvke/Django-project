import sqlite3
import requests
from datetime import datetime
from lxml import etree

# Функция для получения данных о курсах валют на определенную дату
def get_currency_data(date):
    url = f"http://www.cbr.ru/scripts/XML_daily.asp?date_req={date.strftime('%d/%m/%Y')}"
    try:
        # получаем ответ и запрашиваем статус
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Ошибка при запросе данных для даты {date}: {e}")
        return None

    # Записываем ответ
    xml_data = response.content

    # С помощью библиотеки lxml создаем xml дерево с помощью метода fromstring
    tree = etree.fromstring(xml_data)
    # словарь с курсами валют
    currency_data = {'date': date.strftime('%Y-%m-%d')}
    # Список валют, которые мы будем обрабатывать
    currencies = ["AZN", "BYR", "BYN", "EUR", "GEL", "KGS", "KZT", "UAH", "USD", "UZS"]
    for currency in currencies:
        try:
            # Ищем курс валюты и номинал в дереве, используем VunitRate, чтобы получать цену за 1 единицу валюты
            value = tree.xpath(f"//Valute[CharCode='{currency}']/VunitRate/text()")[0].replace(',', '.')

            if currency == "BYN":
                currency_data["BYR"] = float(value)
            else:
                currency_data[currency] = float(value)
        except Exception as e:
            currency_data[currency] = None
    return currency_data

# Функция для генерации диапазона дат с шагом в 1 месяц
def generate_date_range(start_date, end_date):
    date_range = []
    current_date = start_date
    while current_date <= end_date:
        date_range.append(current_date)
        # Переход к первому числу следующего месяца
        if current_date.month == 12:
            current_date = datetime(current_date.year + 1, 1, 1)
        else:
            current_date = datetime(current_date.year, current_date.month + 1, 1)
    return date_range

# Функция для создания базы данных и таблицы
def create_db():
    conn = sqlite3.connect('currency.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS currency_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date DATE NOT NULL,
        AZN REAL,
        BYR REAL,
        EUR REAL,
        GEL REAL,
        KGS REAL,
        KZT REAL,
        UAH REAL,
        USD REAL,
        UZS REAL
    )''')
    conn.commit()
    conn.close()

# Функция для сохранения данных в базу данных
def save_to_db(data):
    conn = sqlite3.connect('currency.db')
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO currency_data (date, AZN, BYR, EUR, GEL, KGS, KZT, UAH, USD, UZS)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (data['date'], data['AZN'], data['BYR'], data['EUR'], data['GEL'],
          data['KGS'], data['KZT'], data['UAH'], data['USD'], data['UZS']))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    # Создание базы данных и таблицы
    create_db()

    # определяем промежуток времени
    start_date = datetime(2003, 1, 1)
    end_date = datetime(2024, 11, 1)

    # Генерируем список интересующих дат
    date_range = generate_date_range(start_date, end_date)

    # Проходим по датам и сохраняем данные в базу
    for date in date_range:
        currency_data = get_currency_data(date)
        if currency_data:
            save_to_db(currency_data)
