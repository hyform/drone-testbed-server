from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings

print("run code for auto discover")

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'design.settings')

app = Celery('design')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
