from django.contrib import admin
from .models import Report, PageContent

class ReportAdmin(admin.ModelAdmin):
    list_display = ('title',)
    search_fields = ('title',)


class PageContentAdmin(admin.ModelAdmin):
    list_display = ('title', 'page')
    search_fields = ('title', 'page')


admin.site.register(Report, ReportAdmin)
admin.site.register(PageContent, PageContentAdmin)