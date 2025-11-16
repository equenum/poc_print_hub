from django.contrib import admin
from django.urls import path
from . import endpoints

urlpatterns = [
    path('admin/', admin.site.urls),
    path('printer/status', endpoints.status, name='status'),
    path('printer/feed', endpoints.feed, name='feed'),
    path('printer/cut', endpoints.cut, name='cut'),
    path('queues/publish', endpoints.publish, name='publish'),
    path('queues/republish', endpoints.republish, name='republish'),
    path('queues/status', endpoints.queue_status, name='queuestatus')
]
