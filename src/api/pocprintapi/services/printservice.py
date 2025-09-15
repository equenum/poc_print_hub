import json

from rest_framework import status
from rest_framework.response import Response
from pocprintapi.models.notifications import NotificationMessage

class PrintService:
    def __init__(self):
        pass

    def process_print_request(self, request_body: bytes):
        body_dict = json.loads(request_body)

        message = NotificationMessage(
            body_dict.get("title"),
            body_dict.get("body"),
            body_dict.get("bodyType"),
            body_dict.get("origin"),
            body_dict.get("timestamp"))
        
        errors = message.validate()
        if len(errors) > 0:
            return Response(f"Invalid request, errors: {", ".join(errors)}", status.HTTP_400_BAD_REQUEST)
        
        # Mock response for testing          
        return Response(
            f"{message.id}, {message.title}, {message.body}, {message.body_type}, {message.origin}, {message.timestamp}", 
            status.HTTP_200_OK)
