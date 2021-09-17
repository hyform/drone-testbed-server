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

class BotConsumer(WebsocketConsumer):
    def connect(self):
        logger.debug("BotConsumer: attempting connection")
        params = parse_qs(self.scope['query_string'].decode('utf8'))
        session_id = params.get('s_id', (None,))[0]
        position_id = params.get('p_id', (None,))[0]
        bot_key = params.get('bot_key', (None,))[0]        

        #Make sure we don't pass this check if both are null/empty
        if bot_key and bot_key == settings.BOT_SECRET_KEY:            
            session = Session.objects.filter(id=session_id).first()
            position = Position.objects.filter(id=position_id).first()
            if session and position:
                self.accept()
                self.session_id = session_id
                self.position_id = position_id
                logger.debug("BotConsumer: connected")

                #TODO Subscribe to channels based on position
                #TODO Potentially subscribe to other channels, to allow bot to see events that happen outside of chat
                # such as new designs/plans that affect them
            else:
                logger.error("Could not connect to BotComsumer")
                if not session:
                    logger.error("Invalid session: " + str(session_id))
                if not position:
                    logger.error("Invalid position: " + str(position_id))
        else:
            logger.error("Could not connect to BotComsumer")
            logger.error("Invalid Bot Key: " + str(bot_key))
    
    def receive(self, text_data):
        logger.debug("BotConsumer: receive")
        logger.debug(str(text_data))
        session = Session.objects.filter(id=self.session_id).first()
        if session:
            logger.debug("Session: " + str(self.session_id) + ": " + session.name)
        else:
            logger.debug("No Session")
        position = Position.objects.filter(id=self.position_id).first()
        if position:
            logger.debug("Position: " + str(self.position_id) + ": " + position.name)
        else:
            logger.debug("No Position")

