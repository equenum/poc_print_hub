import uuid

from datetime import datetime
from typing import Union, List

class NotificationMessage:
    def __init__(self, title: str, body: str, body_type: str, origin: str, timestamp: Union[str, datetime]):
        self.id: uuid.UUID = uuid.uuid4()
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

        if not self._is_none_or_empty(self.body_type) and self.body_type not in [ "PlainText", "KeyValue"]:
            errors.append("Invalid 'bodyType': should be 'PlainText' or 'KeyValue'")

        if self._is_none_or_empty(self.origin):
            errors.append("Required: 'origin'")

        if self.timestamp is None:
            errors.append("Required: 'timestamp'")

        return errors

    def _is_none_or_empty(self, string: str) -> bool:
        return string is None or string.strip() == ""