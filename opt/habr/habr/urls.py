from django.contrib import admin

from habr import settings
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("parse_habr.urls")),
]

