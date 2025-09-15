from django.contrib import admin
from django.urls import path
from . import endpoints

urlpatterns = [
    path('admin/', admin.site.urls),
    path('print', endpoints.print, name='print')
]
