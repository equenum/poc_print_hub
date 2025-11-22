from django.contrib import admin
from django.urls import path
from . import endpoints

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/printer/status', endpoints.status, name='status'),
    path('api/printer/feed', endpoints.feed, name='feed'),
    path('api/printer/cut', endpoints.cut, name='cut'),
    path('api/queues/publish', endpoints.publish, name='publish'),
    path('api/queues/republish', endpoints.republish, name='republish'),
    path('api/queues/status', endpoints.queue_status, name='queuestatus'),
    path('api/tenant/role', endpoints.tenant_role, name='tenantrole')
]
