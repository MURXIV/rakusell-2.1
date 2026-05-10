import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('rakusell')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.task_queues = {
    'default': {'exchange': 'default', 'routing_key': 'default'},
    'messages': {'exchange': 'messages', 'routing_key': 'messages'},
    'ai': {'exchange': 'ai', 'routing_key': 'ai'},
}

app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
