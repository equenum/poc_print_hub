import json

from django.http import HttpRequest
from rest_framework.decorators import api_view
from pocprintapi.services.printservice import PrintService

@api_view(['POST'])
def publish(request: HttpRequest):
    return PrintService().publish(request.body)

@api_view(['GET'])
def status(request: HttpRequest):
    return PrintService().status()

@api_view(['POST'])
def feed(request: HttpRequest):
    body_dict = json.loads(request.body)

    n_times = body_dict.get("n_times", "5")

    return PrintService().feed(n_times)

@api_view(['POST'])
def cut(request: HttpRequest):
    return PrintService().cut()

@api_view(['POST'])
def republish(request: HttpRequest):
    return PrintService().republish_dead_queue_messages()