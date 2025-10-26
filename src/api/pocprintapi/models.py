import uuid
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pocprintapi.settings')
django.setup()

from datetime import datetime
from typing import Union, List
from enum import Enum
from django.db import models
from django.contrib import admin
from django.contrib.auth.hashers import make_password, check_password
from model_utils.tracker import FieldTracker

class NotificationMessage:
    def __init__(self, id: uuid.UUID, title: str, body: str, body_type: str, origin: str, timestamp: Union[str, datetime]):
        self.id: uuid.UUID = id
        self.title: str = title
        self.body: str = body
        self.body_type: str = body_type
        self.origin: str = origin

        if timestamp is None or isinstance(timestamp, datetime):
            self.timestamp: datetime = timestamp
        else:
            self.timestamp: datetime = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")

    def __str__(self):
        return f"origin: {self.origin}, title: {self.title}"
    
    @staticmethod
    def from_json(json_dict):
        return NotificationMessage(
            json_dict.get("id"),
            json_dict.get("title"),
            json_dict.get("body"),
            json_dict.get("bodyType"),
            json_dict.get("origin"),
            json_dict.get("timestamp")
        )
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "title": self.title,
            "body": self.body,
            "bodyType": self.body_type,
            "origin": self.origin,
            "timestamp": str(self.timestamp)
        }
    
    def validate(self) -> List[str]:
        errors = []

        if self._is_none_or_empty(self.title):
            errors.append("Required: 'title'")

        if self._is_none_or_empty(self.body):
            errors.append("Required: 'body'")

        if self._is_none_or_empty(self.body_type):
            errors.append("Required: 'bodyType'")

        if not self._is_none_or_empty(self.body_type) and self.body_type.upper() not in NotificationBodyType.string_values():
            errors.append("Invalid 'bodyType': should be 'PlainText' or 'KeyValue'")

        if self._is_none_or_empty(self.origin):
            errors.append("Required: 'origin'")

        if self.timestamp is None:
            errors.append("Required: 'timestamp'")

        return errors

    def _is_none_or_empty(self, string: str) -> bool:
        return string is None or string.strip() == ""

class NotificationBodyType(Enum):
    PLAINTEXT = 1
    KEYVALUE = 2
    
    @staticmethod
    def string_values():
        return [
            NotificationBodyType.PLAINTEXT.name.upper(),
            NotificationBodyType.KEYVALUE.name.upper()
        ]
    
class TenantRole(models.TextChoices):
    ADMIN = "ADMIN", "Admin"
    USER = "USER", "User"

    @staticmethod
    def string_values():
        return [
            TenantRole.ADMIN.name.upper(),
            TenantRole.USER.name.upper()
        ]

class TenantAuthConfig(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant_id = models.TextField(unique=True)
    role = models.TextField(
        choices=TenantRole.choices,
        default=TenantRole.USER
    )
    token = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tracker = FieldTracker()

    def save(self, *args, **kwargs):
        if not self.pk or self.tracker.has_changed('token'):
            self.token = make_password(self.token)
        super().save(*args, **kwargs)

    def check_token(self, raw_token: str):
        return check_password(raw_token, self.token)

    def __str__(self):
        return f"{self.role} - {self.tenant_id}"
    
admin.site.register(TenantAuthConfig)