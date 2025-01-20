from django.shortcuts import render
from .models import *
import requests
import json
import pandas as pd
from bs4 import BeautifulSoup


def get_pages():
    # Возвращает список страниц, их url и иконку
    return [
        {'url_name': 'index_page', 'name': 'Главная страница', 'icon': 'img/home.png'}, # Главная страница
        {'url_name': 'general_statistics', 'name': 'Общая статистика', 'icon': 'img/statistics.png'}, # Общая статистика
        {'url_name': 'demand', 'name': 'Востребованность', 'icon': 'img/statistics.png'}, # Востребованность
        {'url_name': 'geography', 'name': 'География', 'icon': 'img/statistics.png'}, # География
        {'url_name': 'skills', 'name': 'Навыки', 'icon': 'img/pie.png'}, # Навыки
        {'url_name': 'last_vacancies', 'name': 'Последние вакансии', 'icon': 'img/vacancies.png'}, # Последние вакансии
    ]


def index_page(request):
    # Данные на странице index_page
    contents = PageContent.objects.filter(page='index_page')
    return render(request, 'index.html', {'pages': get_pages(), 'contents': contents})


def general_statistics(request):
    # Данные на странице general_statistics
    reports = Report.objects.filter(category='general_statistics')
    contents = PageContent.objects.filter(page='general_statistics')
    return render(request, 'general_statistics.html', {'pages': get_pages(), 'reports': reports, 'contents': contents})


def demand(request):
    # Данные на странице demand
    reports = Report.objects.filter(category='demand')
    contents = PageContent.objects.filter(page='demand')
    return render(request, 'demand.html', {'pages': get_pages(), 'reports': reports, 'contents': contents})


def geography(request):
    # Данные на странице geography
    reports = Report.objects.filter(category='geography')
    contents = PageContent.objects.filter(page='geography')
    return render(request, 'geography.html', {'pages': get_pages(), 'reports': reports, 'contents' : contents})


def skills(request):
    # Данные на странице skills
    reports = Report.objects.filter(category='skills')
    contents = PageContent.objects.filter(page='skills')
    return render(request, 'skills.html', {'pages': get_pages(), 'reports': reports, 'contents' : contents})


def last_vacancies(request):
    # Данные на странице last_vacancies
    vacancies = get_vacancies()
    reports = Report.objects.filter(category='last_vacancies')
    contents = PageContent.objects.filter(page='last_vacancies')
    return render(request, 'last_vacancies.html', {'pages': get_pages(), 'reports': reports, 'contents' : contents, 'vacancies': vacancies})


def get_vacancies():
    # Возвращает html таблицу с 10 вакансиями 
    try:
        req = requests.get('https://api.hh.ru/vacancies?period=1&per_page=10&text=GameDev&search_field=name&search_field=description&order_by=publication_time')
        data = req.content.decode()
        req.close()
        json_object = json.loads(data)
        df = pd.DataFrame()
        
        for vacancy in json_object['items']:
        
            vacancy_id = vacancy['id']
            vacancy_request = requests.get(f'https://api.hh.ru/vacancies/{vacancy_id}')
            vacancy_data = vacancy_request.content.decode()
            vacancy_request.close()
            vacancy_json = json.loads(vacancy_data)
        
            # Извлекаем данные
            name = vacancy_json['name']
            description = BeautifulSoup(vacancy_json['description'], 'html.parser').text
            key_skills = ', '.join([skill['name'] for skill in vacancy_json['key_skills']])
            key_skills = key_skills if key_skills != '' else '—'
            employer_name = vacancy_json['employer']['name']
        
            salary_from = vacancy_json['salary']['from'] if vacancy_json['salary'] and 'from' in vacancy_json[
                'salary'] else '—'
            salary_to = vacancy_json['salary']['to'] if vacancy_json['salary'] and 'to' in vacancy_json['salary'] else '—'
            salary_currency = vacancy_json['salary']['currency'] if vacancy_json['salary'] and 'currency' in vacancy_json[
                'salary'] else '—'
        
            area_name = vacancy_json['area']['name']
            published_at = vacancy_json['published_at']

            url = vacancy_json['alternate_url']

            # Собираем в словарь
            d = {'name': name,
                'description': f'{description[:100]}...<a href="{url}" target="_blank"> перейти к вакансии</a>',
                'key_skills': key_skills,
                'employer_name': employer_name,
                'salary_from': salary_from,
                'salary_to': salary_to,
                'salary_currency': salary_currency,
                'area_name': area_name,
                'published_at': published_at}
        
            df = df._append(d, ignore_index=True)

        df.index = df.index + 1

        return df.to_html(escape=False)
    except Exception as e:
        return f'<p><i>Каждый совершает ошибки</i><br> <b>{e}</b></p>'  