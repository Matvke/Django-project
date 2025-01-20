import sqlite3
from collections import Counter
from fileinput import close
from matplotlib import pyplot as plt
import pandas as pd
import time
from concurrent.futures import ThreadPoolExecutor
import swifter


def get_currency_data(row):
    """
    Функция для обращения к БД для извлечения данных о валюте
    :param row: df row
    :return: float - переведенная в рубли зп
    """
    date = row['first_day_of_month'].strftime('%Y-%m-%d')
    salary = row['salary']
    salary_currency = row['salary_currency']

    if pd.isna(salary) or pd.isna(salary_currency) or pd.isna(date):
        return None
    if salary_currency == 'RUR':
        return salary

    con = sqlite3.connect('currency.db')
    cur = con.cursor()
    res = cur.execute(f"select {salary_currency} from currency_data where date = '{date}'")
    try:
        result = round(res.fetchone()[0] * salary)
        if result >= 10000000:
            result = None
    except Exception as e:
        result = None
    return result


def get_average_salary(row):
    # Возвращает среднюю зарплату
    salary_from = row['salary_from']
    salary_to = row['salary_to']
    if pd.isna(salary_from) and pd.isna(salary_to):
        return None
    elif pd.isna(salary_from) and not pd.isna(salary_to):
        return salary_to
    elif not pd.isna(salary_from) and pd.isna(salary_to):
        return salary_from
    else:
        return float((salary_from + salary_to) / 2)


def analyze_vacancies(csv):
    df = pd.read_csv(csv)
    print('CSV file read')

    # Вычисление средней зарплаты
    df['salary'] = df.swifter.apply(get_average_salary, axis=1)

    # Преобразование столбца 'published_at' к типу datetime и обработка NaN
    df['published_at'] = pd.to_datetime(df['published_at'], errors='coerce', utc=True)

    # Новый столбец для группировки по году
    df['year'] = df['published_at'].dt.year

    # Новый столбец для запроса к ЦБ по первому числу месяца
    df['first_day_of_month'] = df['published_at'].dt.to_period('M').dt.to_timestamp()

    # Новый столбец зп в рублях
    df['salary_in_rub'] = df.swifter.apply(get_currency_data, axis=1)

    print('Preparation completed')

    # Анализ вакансий
    with ThreadPoolExecutor(max_workers=5) as executor:
        salary_dynamic_future = executor.submit(get_salary_dynamic, df)
        count_dynamic_future = executor.submit(get_count_dynamic, df)
        city_salary_dynamic_future = executor.submit(get_city_salary_dynamic, df)
        city_count_dynamic_future = executor.submit(get_city_count_dynamic, df)
        top20_skills_future = executor.submit(get_top20_skills, df)

        salary_dynamic = salary_dynamic_future.result()
        print('salary_dynamic done')
        count_dynamic = count_dynamic_future.result()
        print('count_dynamic done')
        city_salary_dynamic = city_salary_dynamic_future.result()
        print('city_salary_dynamic done')
        city_count_dynamic = city_count_dynamic_future.result()
        print('city_count_dynamic done')
        top20_skills = top20_skills_future.result()
        print('top20_skills done')
    print('Analyze done')

    return salary_dynamic, count_dynamic, city_salary_dynamic, city_count_dynamic, top20_skills


def create_bar_plot(series, title, xlabel, ylabel):
    # Создать гистограмму
    plt.style.use('ggplot')
    plt.figure(figsize=(10, 6), facecolor='#221D22')
    series.plot(kind='bar', color='#FFBE5C')
    plt.title(label=title, color='white')
    plt.xlabel(xlabel=xlabel, color='white')
    plt.xticks(rotation=90)
    plt.ylabel(ylabel=ylabel, color='white')
    plt.grid(True, color='gray')
    plt.tight_layout()
    plt.gca().set_facecolor('#221D22')
    plt.savefig(f'student_works/{title}.png')
    plt.close()
    #plt.show()


def create_line_plot(series, title, xlabel, ylabel):
    # Создать линейный график
    plt.style.use('ggplot')
    plt.figure(figsize=(13, 6), facecolor='#221D22')
    series.plot(kind='line', marker='o', color='#FFBE5C')
    plt.title(label=title, fontsize=14, color='white')
    plt.xlabel(xlabel=xlabel, color='white')
    plt.ylabel(ylabel=ylabel, color='white')
    plt.grid(True, color='gray')
    plt.xticks(ticks=series.index, labels=series.index.astype(int))
    plt.gca().set_facecolor('#221D22')
    plt.tight_layout()
    plt.savefig(f'student_works/{title}.png')
    plt.close()
    #plt.show()


def create_pie_plot(series, title):
    # Создать круговую диаграмму
    if series.empty:
        return

    def make_autopct(values):
        # Сделать автоматическое форматирование подписей
        def my_autopct(pct):
            total = sum(values)
            val = int(round(pct * total / 100.0))
            return '{p:.0f}%  ({v:d})'.format(p=pct, v=val)
        return my_autopct

    plt.style.use('ggplot')
    plt.figure(figsize=(10, 10), facecolor='#221D22', dpi=100)
    plt.pie(series.values, labels=series.index, autopct=make_autopct(series.values), textprops={'color': 'white' ,'fontsize': 9})
    plt.title(title, color='white')
    plt.tight_layout()
    plt.savefig(f'student_works/{title}.png')
    plt.close()
    #plt.show()


def create_template(series, columns, name):
    # Возвращает html таблицу 
    if series.empty:
        return
    with open(f'student_works/{name}.txt', 'w', encoding='utf-8') as f:
        series = series.to_frame().reset_index(drop=False)
        series.columns = columns
        f.write(series.to_html(index=False))
        close()


def get_salary_dynamic(df):
    """
    Высчитывает динамику зп по годам.
    :param df:
    :return: df[['year', 'salary_in_rub']]
    """
    return df.groupby('year')['salary_in_rub'].mean().round()


def get_count_dynamic(df):
    # Расчитывает динамику количества вакансий
    return df.groupby('year')['name'].count().astype(int)


def get_city_salary_dynamic(df):
    # Расчитывает динамику зарплаты по городам
    city_salary_dynamic = df.groupby('area_name')['salary_in_rub'].mean().round()
    city_salary_dynamic = city_salary_dynamic[
                              city_salary_dynamic.index.isin(
                                  df['area_name'].value_counts()[lambda x: x > len(df) * 0.01].index)
                          ].sort_values(ascending=False)
    return city_salary_dynamic


def get_city_count_dynamic(df):
    # Расчитывает динамику количества вакансий по городам
    city_vacancy_share = df['area_name'].value_counts(normalize=True) * 100
    city_vacancy_share = city_vacancy_share[
                              city_vacancy_share.index.isin(
                                  df['area_name'].value_counts()[lambda x: x > len(df) * 0.01].index)
                          ]
    other_cities = 100 - city_vacancy_share.sum()
    city_vacancy_share['Другие'] = other_cities
    return city_vacancy_share.round(2).sort_values(ascending=False)


def process_skills_group(skills):
    # Счет топ 20 вакансий в группе
    all_skills = '\n'.join(skills.dropna()).split('\n')
    cleaned_skills = [skill.strip().replace('\r', '').replace('\n', '') for skill in all_skills]
    print('Group done')
    return Counter(cleaned_skills).most_common(20)


def get_top20_skills(df):
    # Топ20 по всем годам
    grouped = df.groupby('year')['key_skills']

    results = []

    # Используем ThreadPoolExecutor для параллельной обработки групп
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            executor.submit(process_skills_group, group)
            for _, group in grouped
            if not group.dropna().empty
        ]
        for future in futures:
            results.append(future.result())

    years = [year for year, group in grouped if not group.dropna().empty]
    result_df = pd.DataFrame({'year': years, 'top_20_skills': results})
    return result_df


def filter_and_save_csv(input_csv, output_csv, keywords, column_name='name'):
    """
    Функция для фильтрации и сохранения CSV-файла на основе ключевых слов.

    :param input_csv: Путь к исходному CSV-файлу.
    :param output_csv: Путь для сохранения отфильтрованного CSV-файла.
    :param keywords: Список ключевых слов для фильтрации.
    :param column_name: Название столбца для фильтрации. По умолчанию 'name'.
    """
    df = pd.read_csv(input_csv)
    valid_names = '|'.join(keywords)
    filtered_df = df[df[column_name].str.contains(valid_names, case=False, na=False)]
    filtered_df.to_csv(output_csv, index=False)


if __name__ == '__main__':
    print('Start program')
    start_time = time.time()

    full_csv = 'vacancies_2024.csv'
    filtered_csv = 'filtered_vacancies.csv'
    keywords = ['Разработчик игр', 'GameDev', 'game', 'unity', 'игр', 'unreal']
    filter_and_save_csv(full_csv, filtered_csv, keywords)

    salary_dynamic, count_dynamic, city_salary_dynamic, city_count_dynamic, top20_skills = analyze_vacancies(full_csv)
    filtered_salary_dynamic, filtered_count_dynamic,filtered_city_salary_dynamic, filtered_city_count_dynamic, filtered_top20_skills = analyze_vacancies(filtered_csv)

    # Отрисовка графиков по всем вакансиям

    create_line_plot(salary_dynamic, 'Динамика средней зарплаты по годам', 'Год',
                     'Средняя зарплата в рублях')
    create_template(salary_dynamic, ['Год', 'Средняя зарплата в рублях'],
                    'Динамика средней зарплаты по годам')

    create_bar_plot(count_dynamic, 'Динамика количества вакансий по годам', 'Год',
                    'Количество вакансий')
    create_template(count_dynamic, ['Год', 'Количество вакансий'],
                    'Динамика количества вакансий по годам')

    create_bar_plot(city_salary_dynamic, 'Средняя зарплата по городам', 'Город',
                    'Средняя зарплата в рублях')
    create_template(city_salary_dynamic, ['Город', 'Средняя зарплата в рублях'],
                    'Средняя зарплата по городам')

    create_pie_plot(city_count_dynamic, 'Доли вакансий по городам')
    create_template(city_count_dynamic, ['Город', 'Доля вакансий'], 'Доли вакансий по городам')

    for year, skills in top20_skills.values:
        skills_series = pd.Series(dict(skills))
        create_pie_plot(skills_series, f'Навыки за {year} год')
        create_template(skills_series, ['Навык', 'Частота'], f'Навыки за {year} год')
        print(f"top_20_skills_for_{year} plot and template created")

    print('full analytics charts done')
    # Отрисовка графиков по вакансиям GameDev

    create_line_plot(filtered_salary_dynamic, 'Динамика средней зарплаты по годам профессии GameDev', 'Год',
                     'Средняя зарплата в рублях')
    create_template(filtered_salary_dynamic, ['Год', 'Средняя зарплата в рублях'],
                    'Динамика средней зарплаты по годам профессии GameDev')
    print('create_line plot and template done')

    create_bar_plot(filtered_count_dynamic, 'Динамика количества вакансий по годам профессии GameDev', 'Год',
                    'Количество вакансий')
    create_template(filtered_count_dynamic, ['Год', 'Количество вакансий'],
                    'Динамика количества вакансий по годам профессии GameDev')
    print('count_dynamic_bar plot and template done')

    create_bar_plot(filtered_city_salary_dynamic, 'Средняя зарплата по городам профессии GameDev', 'Город',
                    'Средняя зарплата в рублях')
    create_template(filtered_city_salary_dynamic, ['Город', 'Средняя зарплата в рублях'],
                    'Средняя зарплата по городам профессии GameDev')
    print('city_salary_dynamic_bar plot and template done')

    create_pie_plot(filtered_city_count_dynamic, 'Доли вакансий по городам профессии GameDev')
    create_template(filtered_city_count_dynamic, ['Город', 'Доля вакансий'], 'Доли вакансий по городам профессии GameDev')
    print('city_count_dynamic_bar plot and template done')

    for year, skills in filtered_top20_skills.values:
        skills_series = pd.Series(dict(skills))
        create_pie_plot(skills_series, f'Навыки за {year} год профессии GameDev')
        create_template(skills_series, ['Навык', 'Частота'], f'Навыки за {year} год профессии GameDev')
        print(f"top_20_skills_for_{year} plot and template created")

    print('filtered analytics charts done')
    print('All charts have been successfully created and saved')

    end_time = time.time()
    execution_time = end_time - start_time

    print(f"Время выполнения программы: {execution_time} секунд")
