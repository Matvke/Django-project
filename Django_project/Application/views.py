from django.shortcuts import render
from .models import *

def get_pages():
    return [
        {'url_name': 'index_page', 'name': 'Главная страница'}, # Главная страница
        {'url_name': 'general_statistics', 'name': 'Общая статистика'}, # Общая статистика
        {'url_name': 'demand', 'name': 'Востребованность'}, # Востребованность
        {'url_name': 'geography', 'name': 'География'}, # География
        {'url_name': 'skills', 'name': 'Навыки'}, # Навыки
        {'url_name': 'last_vacancies', 'name': 'Последние вакансии'}, # Последние вакансии
    ]

def index_page(request):
    return render(request, 'index.html', {'pages': get_pages()})

def general_statistics(request):
    reports = Report.objects.filter(category='general_statistics')
    return render(request, 'general_statistics.html', {'pages': get_pages(), 'reports': reports})

def demand(request):
    reports = Report.objects.filter(category='demand')
    return render(request, 'demand.html', {'pages': get_pages(), 'reports': reports})

def geography(request):
    reports = Report.objects.filter(category='geography')
    return render(request, 'geography.html', {'pages': get_pages(), 'reports': reports})

def skills(request):
    reports = Report.objects.filter(category='skills')
    return render(request, 'skills.html', {'pages': get_pages(), 'reports': reports})

def last_vacancies(request):
    reports = Report.objects.filter(category='last_vacancies')
    return render(request, 'last_vacancies.html', {'pages': get_pages(), 'reports': reports})