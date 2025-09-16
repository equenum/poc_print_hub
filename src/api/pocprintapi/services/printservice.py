import json
import pika

from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from pocprintapi.models.notifications import NotificationMessage

class PrintService:
    def process_print_request(self, request_body: bytes):
        body_dict = json.loads(request_body)

        message = NotificationMessage(
            body_dict.get("title"),
            body_dict.get("body"),
            body_dict.get("bodyType"),
            body_dict.get("origin"),
            body_dict.get("timestamp")
        )
        
        errors = message.validate()
        if len(errors) > 0:
            return Response(
                f"Invalid request, errors: {", ".join(errors)}", 
                status.HTTP_400_BAD_REQUEST
            )
        
        try:
            self._publish_message(message)
        except Exception as ex:
            return Response(
                f"Failed to publish message to RabbitMQ, error: {ex}", 
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        return Response(
            f"Message id: {message.id}", 
            status.HTTP_200_OK
        )
    
    def _publish_message(self, message: NotificationMessage):
        credentials = pika.PlainCredentials(
            settings.POC_PRINT_HUB_RABBIT_MQ_USERNAME, 
            settings.POC_PRINT_HUB_RABBIT_MQ_PASSWORD
        )
        
        parameters = pika.ConnectionParameters(
            host=settings.POC_PRINT_HUB_RABBIT_MQ_HOST,
            credentials=credentials
        )

        try:
            connection = pika.BlockingConnection(parameters)
            channel = connection.channel()

            channel.queue_declare(
                queue=settings.POC_PRINT_HUB_RABBIT_MQ_QUEUE_NAME, 
                durable=settings.POC_PRINT_HUB_RABBIT_MQ_QUEUE_DURABLE
            )

            channel.basic_publish(
                exchange="",
                routing_key=settings.POC_PRINT_HUB_RABBIT_MQ_QUEUE_NAME,
                body=json.dumps(message.to_dict())
            )
        finally:
            connection.close()    
        