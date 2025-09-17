import json
import pika

from django.conf import settings
from escpos import printer
from rest_framework import status
from rest_framework.response import Response
from pocprintapi.models.notifications import NotificationMessage

class PrintService:
    MIN_FEED_N: int = 5
    MAX_FEED_N: int = 255

    def print(self, request_body: bytes) -> Response:
        """Publishes notification message to RabbitMQ"""
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
    
    def status(self) -> Response:
        """Fetches printer status: online, paper status"""
        try:
            net_print = printer.Network(settings.POC_PRINT_HUB_PRINTER_HOST)

            is_online = net_print.is_online()
            paper_status = net_print.paper_status()

            paper_status_text = ""
            match paper_status:
                case 0:
                    paper_status_text = "Empty"
                case 1:
                    paper_status_text = "Near End"
                case 2:
                    paper_status_text = "Plenty"
                case _:
                    paper_status_text = "Invalid"

        except Exception as ex:
            return Response(
                f"Failed to fetch printer status, error: {ex}", 
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        finally:
            if net_print is not None:
                net_print.close()

        return Response(
            f"Online: {is_online}, Paper status: {paper_status_text}", 
            status.HTTP_200_OK
        )

    def feed(self, n_times: str) -> Response:
        """Feeds printer paper *n* times. n should be 5 <= x <= 255"""
        try:
            n_times_int = int(n_times)
        except ValueError:
            return Response(
                f"Invalid 'n_times' type: should be 'int'", 
                status.HTTP_400_BAD_REQUEST
            )
        
        if n_times_int < self.MIN_FEED_N or n_times_int > self.MAX_FEED_N:
            return Response(
                f"'n_times' out of range: should be {self.MIN_FEED_N} <= x <= {self.MAX_FEED_N}", 
                status.HTTP_400_BAD_REQUEST
            )

        try:
            net_print = printer.Network(settings.POC_PRINT_HUB_PRINTER_HOST)
            net_print.print_and_feed(n_times_int)
        except Exception as ex:
            return Response(
                f"Failed to send 'Feed' command to printer, error: {ex}", 
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        finally:
            if net_print is not None:
                net_print.close()

        return Response(
            f"Command 'Feed' successfully sent to printer", 
            status.HTTP_200_OK
        )

    def cut(self) -> Response:
        """Cuts printer paper. Paper is fed n*6 times before being cut"""
        try:
            net_print = printer.Network(settings.POC_PRINT_HUB_PRINTER_HOST)
            net_print.cut()
        except Exception as ex:
            return Response(
                f"Failed to send 'Cut' command to printer, error: {ex}", 
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        finally:
            if net_print is not None:
                net_print.close()

        return Response(
            f"Command 'Cut' successfully sent to printer", 
            status.HTTP_200_OK
        )
    
    def _publish_message(self, message: NotificationMessage) -> None:
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
                body=json.dumps(message.to_dict()),
                properties=pika.BasicProperties(
                    delivery_mode=pika.DeliveryMode.Persistent
                )
            )
        finally:
            if connection is not None:
                connection.close()    
        