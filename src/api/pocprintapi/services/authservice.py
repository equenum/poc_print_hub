from typing import List
from pocprintapi.models import TenantAuthConfig, TenantRole
from django.conf import settings

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
        
    def _is_none_or_empty(self, string: str) -> bool:
        return string is None or string.strip() == ""