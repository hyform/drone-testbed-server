from celery import Celery
from celery import shared_task
from celery.utils.log import get_task_logger
from exper.models import UserPosition, Session, User
from design.celery import app
from django.conf import settings
import websocket
import threading
import time

