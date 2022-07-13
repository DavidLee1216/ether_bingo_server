import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ether_bingo_server.settings')

app = Celery('ether_bingo_server')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.update(result_expires=60)
app.autodiscover_tasks()
