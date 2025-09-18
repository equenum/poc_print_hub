from enum import Enum

class NotificationBodyType(Enum):
    PLAINTEXT = 1
    KEYVALUE = 2

    def string_values():
        return [
            NotificationBodyType.PLAINTEXT.name,
            NotificationBodyType.KEYVALUE.name
        ]