from django.shortcuts import render

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
    return render(request, 'general_statistics.html', {'pages': get_pages()})

def demand(request):
    return render(request, 'demand.html', {'pages': get_pages()})

def geography(request):
    return render(request, 'geography.html', {'pages': get_pages()})

def skills(request):
    return render(request, 'skills.html', {'pages': get_pages()})

def last_vacancies(request):
    return render(request, 'last_vacancies.html', {'pages': get_pages()})
