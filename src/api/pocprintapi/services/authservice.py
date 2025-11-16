from typing import List
from pocprintapi.models import TenantAuthConfig, TenantRole
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response

class AuthService:
    def is_authorized(self, target_tenant_id: str, tenant_token: str, allowed_roles: List[TenantRole]) -> bool:
        if not settings.POC_PRINT_HUB_TENANT_AUTH_ENABLED:
            return True
        
        if self._is_none_or_empty(target_tenant_id):
            print("Empty tenant id")
            return False
        
        if self._is_none_or_empty(tenant_token):
            print("Empty tenant token")
            return False
        
        try:
            tenant = TenantAuthConfig.objects.get(tenant_id=target_tenant_id)

            if not tenant.check_token(tenant_token):
                return False

            if self._is_none_or_empty(tenant.role):
                print(f"Invalid tenant role, tenant id: {target_tenant_id}.")
                return False
            
            str_allowed_roles = []

            for role in allowed_roles:
                str_allowed_roles.append(role.name.upper())

            return tenant.role in str_allowed_roles
        except TenantAuthConfig.DoesNotExist:
            print(f"Tenant not found: {target_tenant_id}.")
            return False
        
    def get_tenant_role(self, target_tenant_id: str) -> Response:
        if self._is_none_or_empty(target_tenant_id):
            return Response(
                {
                    "message": "Tenant id cannot be empty."
                }, 
                status.HTTP_400_BAD_REQUEST
            )
        
        try:
            tenant = TenantAuthConfig.objects.get(tenant_id=target_tenant_id)

            return Response(
                {
                    "tenantId": tenant.tenant_id,
                    "role": tenant.role.upper()
                }, 
                status.HTTP_200_OK
            )
        except TenantAuthConfig.DoesNotExist:
            return Response(
                {
                    "message": f"Tenant not found, id: {target_tenant_id}."
                }, 
                status.HTTP_404_NOT_FOUND
            )
        
    def _is_none_or_empty(self, string: str) -> bool:
        return string is None or string.strip() == ""