from django.http import HttpRequest
from rest_framework.decorators import api_view
from pocprintapi.services.printservice import PrintService

@api_view(['POST'])
def print(request: HttpRequest):
    service = PrintService()
    return service.process_print_request(request.body)