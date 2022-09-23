import datetime

from django.contrib import admin
from rangefilter.filters import DateRangeFilter

from .models import Articles

@admin.register(Articles)
class ArticlesAdmin(admin.ModelAdmin):
    list_filter = (
        ('date_published', DateRangeFilter), "date_published"
    )

    def get_rangefilter_created_at_default(self, request):
        return datetime.date.today, datetime.date.today

    def get_rangefilter_created_at_title(self, request, field_path):
        return 'custom title'
