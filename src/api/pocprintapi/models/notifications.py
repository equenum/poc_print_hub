from datetime import datetime

class NotificationMessage:
    def __init__(self, title: str, body: str, body_type: str, origin: str, timestamp: datetime):
        self.title = title
        self.body = body
        self.body_type = body_type
        self.origin = origin
        self.timestamp = timestamp

    def __str__(self):
        return f"origin: {self.origin}, title: {self.title}"