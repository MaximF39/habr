from django.contrib import admin

from .models import *

@admin.register(Articles)
class ArticlesAdmin(admin.ModelAdmin):
    pass

