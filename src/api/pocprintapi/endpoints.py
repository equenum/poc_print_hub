import json

from django.http import HttpRequest
from django.conf import settings
from typing import List
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status as response_status
from pocprintapi.services.printservice import PrintService
from pocprintapi.services.authservice import AuthService
from pocprintapi.models import TenantRole

@api_view(['POST'])
def publish(request: HttpRequest):
    if _is_request_authorized(request, [TenantRole.ADMIN, TenantRole.USER]):
        return PrintService().publish(request.body)
    
    return _response_unauthorized()

@api_view(['GET'])
def status(request: HttpRequest):
    if _is_request_authorized(request, [TenantRole.ADMIN]):
        return PrintService().status()
    
    return _response_unauthorized()

@api_view(['POST'])
def feed(request: HttpRequest):
    if _is_request_authorized(request, [TenantRole.ADMIN]):
        body_dict = json.loads(request.body)
        n_times = body_dict.get("n_times", "5")
        return PrintService().feed(n_times)
    
    return _response_unauthorized()

@api_view(['POST'])
def cut(request: HttpRequest):
    if _is_request_authorized(request, [TenantRole.ADMIN]):
        return PrintService().cut()

    return _response_unauthorized()

@api_view(['POST'])
def republish(request: HttpRequest):
    if _is_request_authorized(request, [TenantRole.ADMIN]):
        return PrintService().republish_dead_queue_messages()

    return _response_unauthorized()

def _is_request_authorized(request: HttpRequest, allowed_roles: List[str]):
    tenant_id = request.headers.get(settings.POC_PRINT_HUB_TENANT_ID_HEADER) 
    tenant_token = request.headers.get(settings.POC_PRINT_HUB_TENANT_TOKEN_HEADER) 

    return AuthService().is_authorized(tenant_id, tenant_token, allowed_roles)

def _response_unauthorized():
    return Response(
        "Request Unauthorized", 
        response_status.HTTP_401_UNAUTHORIZED
    )