import json
import pika
import uuid

from typing import List
from django.conf import settings
from escpos import printer
from rest_framework import status
from rest_framework.response import Response
from pocprintapi.models.notifications import NotificationMessage
from pocprintapi.models.constants import NotificationBodyType

class PrintService:
    MIN_FEED_N: int = 5
    MAX_FEED_N: int = 255

    def publish(self, request_body: bytes) -> Response:
        """Publishes notification message to RabbitMQ"""
        body_dict = json.loads(request_body)

        message = NotificationMessage.from_json(body_dict)
        message.id = uuid.uuid4()
        
        errors = message.validate()
        if len(errors) > 0:
            return Response(
                f"Invalid request, errors: {", ".join(errors)}", 
                status.HTTP_400_BAD_REQUEST
            )
        
        try:
            self._publish_message(
                message,
                settings.POC_PRINT_HUB_RABBIT_MQ_QUEUE_NAME,
                settings.POC_PRINT_HUB_RABBIT_MQ_QUEUE_DURABLE
            )
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

    def process_queue_messages(self) -> None:
        if not self._is_printer_available():
            print(f'Failed to process messages, error: printer not available')
            return
        
        parameters = self._build_connection_parameters()

        try:
            connection = pika.BlockingConnection(parameters)
            channel = connection.channel()

            print_queue = channel.queue_declare(
                queue=settings.POC_PRINT_HUB_RABBIT_MQ_QUEUE_NAME, 
                durable=settings.POC_PRINT_HUB_RABBIT_MQ_QUEUE_DURABLE
            )

            message_count = print_queue.method.message_count
            processed_message_count = 0

            if message_count == 0:
                print(f"Nothing to process: {settings.POC_PRINT_HUB_RABBIT_MQ_QUEUE_NAME} queue is empty")
                return

            channel.queue_declare(
                queue=settings.POC_PRINT_HUB_RABBIT_MQ_DEAD_QUEUE_NAME, 
                durable=settings.POC_PRINT_HUB_RABBIT_MQ_DEAD_QUEUE_DURABLE
            )

            for method_frame, properties, body in channel.consume(settings.POC_PRINT_HUB_RABBIT_MQ_QUEUE_NAME):
                try:
                    self._print_message(body)
                except Exception as ex:
                    print(
                        f"Failed to process {settings.POC_PRINT_HUB_RABBIT_MQ_QUEUE_NAME} queue message: {ex}. "\
                        f"Delivery properties: {method_frame}. Publishing to error queue."
                    )
                    channel.basic_publish(
                        exchange="",
                        routing_key=settings.POC_PRINT_HUB_RABBIT_MQ_DEAD_QUEUE_NAME,
                        body=json.dumps(json.loads(body)),
                        properties=pika.BasicProperties(
                            delivery_mode=pika.DeliveryMode.Persistent
                        )
                    )

                channel.basic_ack(method_frame.delivery_tag)

                processed_message_count += 1
                message_count -= 1

                if message_count == 0 or processed_message_count >= settings.POC_PRINT_HUB_RABBIT_MQ_QUEUE_BATCH_SIZE:
                    break
            
            channel.cancel()
        finally:
            if connection is not None:
                channel.close()
                connection.close()

    def republish_dead_queue_messages(self) -> Response:
        parameters = self._build_connection_parameters()

        try:
            connection = pika.BlockingConnection(parameters)
            channel = connection.channel()

            dead_letter_queue = channel.queue_declare(
                queue=settings.POC_PRINT_HUB_RABBIT_MQ_DEAD_QUEUE_NAME, 
                durable=settings.POC_PRINT_HUB_RABBIT_MQ_DEAD_QUEUE_DURABLE
            )

            message_count = dead_letter_queue.method.message_count
            republished_message_count = 0

            if message_count == 0:
                return Response(
                    f"Nothing to process: {settings.POC_PRINT_HUB_RABBIT_MQ_DEAD_QUEUE_NAME} queue is empty", 
                    status.HTTP_200_OK
            )

            channel.queue_declare(
                queue=settings.POC_PRINT_HUB_RABBIT_MQ_QUEUE_NAME, 
                durable=settings.POC_PRINT_HUB_RABBIT_MQ_QUEUE_DURABLE
            )

            failed_messages = []

            for method_frame, properties, body in channel.consume(settings.POC_PRINT_HUB_RABBIT_MQ_DEAD_QUEUE_NAME):
                try:
                    channel.basic_publish(
                        exchange="",
                        routing_key=settings.POC_PRINT_HUB_RABBIT_MQ_QUEUE_NAME,
                        body=json.dumps(json.loads(body)),
                        properties=pika.BasicProperties(
                            delivery_mode=pika.DeliveryMode.Persistent
                        )
                    )
                    republished_message_count += 1
                except Exception as ex:
                    print(
                        f"Failed to process {settings.POC_PRINT_HUB_RABBIT_MQ_DEAD_QUEUE_NAME} queue message: {ex}. "\
                        f"Delivery properties: {method_frame}. Republishing to error queue."
                    )
                    failed_messages.append(json.dumps(json.loads(body)))

                channel.basic_ack(method_frame.delivery_tag)
                message_count -= 1

                if message_count == 0:
                    break

            for message in failed_messages:
                channel.basic_publish(
                    exchange="",
                    routing_key=settings.POC_PRINT_HUB_RABBIT_MQ_DEAD_QUEUE_NAME,
                    body=message,
                    properties=pika.BasicProperties(
                        delivery_mode=pika.DeliveryMode.Persistent
                    )
                )

            return Response(
                f"Command 'Republish Dead Letter messages' completed. "\
                f"Republished: {republished_message_count}, failed: {len(failed_messages)}.", 
                status.HTTP_200_OK
            )
        finally:
            if connection is not None:
                channel.close()
                connection.close()

    def _print_message(self, body) -> None:
        body_dict = json.loads(body)
        message = NotificationMessage.from_json(body_dict)

        try:
            net_print = printer.Network(settings.POC_PRINT_HUB_PRINTER_HOST)

            # header
            net_print.textln(settings.POC_PRINT_HUB_PRINTER_MESSAGE_SEPARATOR)
            net_print.textln(f"title: {message.title}")

            # body
            match message.body_type.upper():
                case NotificationBodyType.KEYVALUE.name:
                    for body_print_line in self._build_key_value_body_messages(message):
                        net_print.textln(body_print_line)
                case NotificationBodyType.PLAINTEXT.name:
                    net_print.textln(self._build_plain_text_body_message(message))
                case _:
                    net_print.textln(self._build_plain_text_body_message(message))
            
            # attributes
            net_print.textln(f"origin: {message.origin}")
            net_print.textln(f"timestamp: {message.timestamp}")
        finally:
            if net_print is not None:
                net_print.close()

    def _is_printer_available(self) -> bool:
        try:
            net_print = printer.Network(settings.POC_PRINT_HUB_PRINTER_HOST)
            is_online = net_print.is_online()

            if not settings.POC_PRINT_HUB_PRINTER_CHECK_PAPER_STATUS:
                return is_online

            is_paper_plenty = net_print.paper_status() == 2 # Plenty (Paper is adequate)
            return is_online and is_paper_plenty
        except Exception as ex:
            print(f"Failed to fetch printer availability status, error: {ex}")
            return False
        finally:
            if net_print is not None:
                net_print.close()

    def _build_key_value_body_messages(self, message: NotificationMessage) -> List[str]:
        body_print_lines = []
        body_messages = json.loads(message.body)

        for key, value in body_messages.items():
            body_print_lines.append(f"{key}: {value}")

        return body_print_lines
    
    def _build_plain_text_body_message(self, message: NotificationMessage) -> str:
        return f"body: {message.body}"

    def _publish_message(self, message: NotificationMessage, queue_name: str, queue_durable: bool) -> None:
        parameters = self._build_connection_parameters()

        try:
            connection = pika.BlockingConnection(parameters)
            channel = connection.channel()

            channel.queue_declare(
                queue=queue_name, 
                durable=queue_durable
            )

            channel.basic_publish(
                exchange="",
                routing_key=queue_name,
                body=json.dumps(message.to_dict()),
                properties=pika.BasicProperties(
                    delivery_mode=pika.DeliveryMode.Persistent
                )
            )
        finally:
            if connection is not None:
                connection.close()

    def _build_connection_parameters(self) -> pika.ConnectionParameters:
        return pika.ConnectionParameters(
            host=settings.POC_PRINT_HUB_RABBIT_MQ_HOST,
            credentials=pika.PlainCredentials(
                settings.POC_PRINT_HUB_RABBIT_MQ_USERNAME, 
                settings.POC_PRINT_HUB_RABBIT_MQ_PASSWORD
            )
        )