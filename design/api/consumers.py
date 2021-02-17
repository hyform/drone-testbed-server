# api/consumers.py
from asgiref.sync import async_to_sync
from django.db.models import Q
from channels.generic.websocket import WebsocketConsumer
from django.contrib.auth.models import User
from exper.models import ChannelPosition, Message, Channel, DigitalTwin
from exper.models import SessionTeam, UserPosition, Session
from repo.models import DataLog, DesignTeam, Profile
from ai.agents.adaptive_team_ai_updated_planner import AdaptiveTeamAIUpdatedPlanner
from exper.serializers import DigitalTwinSerializer
from urllib.parse import parse_qs
from collections import OrderedDict
from django.conf import settings
import json
import bleach

class APIConsumer(WebsocketConsumer):
    def connect(self):
        user = self.scope['user']
        if user.profile.is_experimenter() or user.profile.is_mediator():
            self.accept()
            self.send(text_data=json.dumps({
                'type' : 'twin.start',
                'message' : 172,
                'sender' : 'System',
                'channel' : 'twin'
            }))

    #TODO: get reconnection conditions
    #def disconnect(self, close_code):

    # called when owner of this connection sends something over their websocket
    # these should all be commands in this package
    def receive(self, text_data):
        user = self.scope["user"]

        text_data_json = json.loads(text_data)
        message_type = str(text_data_json['type'])
        channel_id = str(text_data_json['channel'])
        message = bleach.clean(text_data_json['message'])
        sender_string = self.username

        if user.profile.is_experimenter():
            if channel_id == "twin":
                if settings.DIGITAL_TWIN_ENABLED:
                    if message_type == "twin.start":
                        session_id = int(message)
                        session = Session.objects.filter(id=session_id).first()
                        if session:
                            digital_twin_setups = get_digital_twin_for_session(session_id)
                            t = AdaptiveTeamAIUpdatedPlanner(session, digital_twin_setups)

    # message templates
    def message_template(self, event):
        message = event['message']
        sender = event['sender']
        channel = event['channel']
        type = event['type']
        # send message to websocket
        self.send(text_data=json.dumps({
            'message': message,
            'sender': sender,
            'channel': channel,
            'type': type
        }))

    # messages
    # called when sending something back to the websocket client

    #TODO add messages for event 'subscriptions'

    #TODO: example
    def twin_start(self, event):
        self.message_template(event)

# helpers
def get_digital_twin_for_session(session_id):
    session_user_positions = []
    user_positions = UserPosition.objects.all()     # for some reason , filter does not work, fix this
    for user in user_positions:
        if user.session.id == session_id:
            session_user_positions.append(user)

    digital_twin_setups = []
    # query or create digital twin objects
    for user in session_user_positions:
        digital_twin_setup = DigitalTwin.objects.filter(user_position=user)
        if len(digital_twin_setup) == 0:
            new_setup = DigitalTwin.objects.create(user_position=user)
            new_setup.save()
            digital_twin_setups.append(new_setup)
        else:
            digital_twin_setups.append(digital_twin_setup[0])

    return digital_twin_setups