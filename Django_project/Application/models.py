from django.db import models

class Report(models.Model):
    CATEGORY_CHOICES = [
        ('general_statistics', 'Общая статистика'),
        ('demand', 'Востребованность'),
        ('geography', 'География'),
        ('skills', 'Навыки'),
        ('last_vacancies', 'Последние вакансии'),
    ]
        
    title = models.CharField(max_length=200)
    chart = models.ImageField(upload_to='charts/')
    table_html = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES,  default='general_statistics')

    def __str__(self):
        return self.title


class PageContent(models.Model):
    PAGE_CHOICES = [
        ('index_page', 'Главная страница'),
        ('general_statistics', 'Общая статистика'),
        ('demand', 'Востребованность'),
        ('geography', 'География'),
        ('skills', 'Навыки'),
        ('last_vacancies', 'Последние вакансии'),
    ]

    title = models.CharField(max_length=200)
    html_content = models.TextField()
    page = models.CharField(max_length=50, choices=PAGE_CHOICES, default='index_page')

    def __str__(self):
        return self.title