import os

from django.conf import settings
from celery import Celery
from celery.exceptions import MaxRetriesExceededError

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pocprintapi.settings')

app = Celery('pocprintapi')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.task_time_limit = settings.POC_PRINT_HUB_QUEUE_TIME_LIMIT_SEC

@app.on_after_configure.connect
def setup_periodic_tasks(sender: Celery, **kwargs):
    sender.add_periodic_task(
        settings.POC_PRINT_HUB_QUEUE_SCHEDULE_SEC, 
        process_queue_messages.s(), 
        name=f'process queue messages every {settings.POC_PRINT_HUB_QUEUE_SCHEDULE_SEC}s'
    )

    sender.add_periodic_task(
        settings.POC_PRINT_HUB_DEAD_QUEUE_SCHEDULE_SEC, 
        process_dead_queue_messages.s(), 
        name=f'process dead queue messages every {settings.POC_PRINT_HUB_DEAD_QUEUE_SCHEDULE_SEC}s'
    )

@app.task(
    bind=True, 
    ignore_result=True, 
    max_retries=settings.POC_PRINT_HUB_QUEUE_MAX_RETRIES, 
    default_retry_delay=settings.POC_PRINT_HUB_QUEUE_RETRY_DELAY_SEC
)
def process_queue_messages(self):
    try:
        print("Processing queue messages")
    except Exception as ex:
        try:
            print(f"Retrying task: {self.name}")
            self.retry(exc=ex)
        except MaxRetriesExceededError:
            print(f"Max task retries hit: {self.name}")

@app.task(
    bind=True, 
    ignore_result=True, 
    max_retries=settings.POC_PRINT_HUB_DEAD_QUEUE_MAX_RETRIES, 
    default_retry_delay=settings.POC_PRINT_HUB_DEAD_QUEUE_RETRY_DELAY_SEC
)
def process_dead_queue_messages(self):
    try:
        print("Processing dead queue messages")
    except Exception as ex:
        try:
            print(f"Retrying task: {self.name}")
            self.retry(exc=ex)
        except MaxRetriesExceededError:
            print(f"Max task retries hit: {self.name}")