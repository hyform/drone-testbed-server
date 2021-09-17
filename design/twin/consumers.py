# api/consumers.py
from asgiref.sync import async_to_sync
from django.db.models import Q
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
from django.contrib.auth.models import User
from exper.models import SessionTeam, UserPosition, Session, Position
from repo.models import DataLog, DesignTeam, Profile
from urllib.parse import parse_qs
from collections import OrderedDict
from django.conf import settings
from rest_framework.authtoken.models import Token
import json
import bleach
import logging

logger = logging.getLogger(__name__)

class TwinConsumer(WebsocketConsumer):
    def connect(self):
        logger.debug("TwinConsumer: attempting connection")
        
    
    def receive(self, text_data):
        logger.debug("TwinConsumer: receive")
        
