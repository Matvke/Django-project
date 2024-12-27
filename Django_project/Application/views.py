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
    contents = PageContent.objects.filter(page='index_page')
    return render(request, 'index.html', {'pages': get_pages(), 'contents': contents})

def general_statistics(request):
    reports = Report.objects.filter(category='general_statistics')
    contents = PageContent.objects.filter(page='general_statistics')
    return render(request, 'general_statistics.html', {'pages': get_pages(), 'reports': reports, 'contents': contents})

def demand(request):
    reports = Report.objects.filter(category='demand')
    contents = PageContent.objects.filter(page='demand')
    return render(request, 'demand.html', {'pages': get_pages(), 'reports': reports, 'contents': contents})

def geography(request):
    reports = Report.objects.filter(category='geography')
    contents = PageContent.objects.filter(page='geography')
    return render(request, 'geography.html', {'pages': get_pages(), 'reports': reports, 'contents' : contents})

def skills(request):
    reports = Report.objects.filter(category='skills')
    contents = PageContent.objects.filter(page='skills')
    return render(request, 'skills.html', {'pages': get_pages(), 'reports': reports, 'contents' : contents})

def last_vacancies(request):
    reports = Report.objects.filter(category='last_vacancies')
    contents = PageContent.objects.filter(page='last_vacancies')
    return render(request, 'last_vacancies.html', {'pages': get_pages(), 'reports': reports, 'contents' : contents})