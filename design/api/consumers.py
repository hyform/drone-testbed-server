# api/consumers.py
from asgiref.sync import async_to_sync
from django.db.models import Q
from channels.generic.websocket import WebsocketConsumer
from django.contrib.auth.models import User
from exper.models import DigitalTwin
from exper.models import SessionTeam, UserPosition, Session
from repo.models import DataLog, DesignTeam, Profile
from ai.agents.adaptive_team_ai_updated_planner import AdaptiveTeamAIUpdatedPlanner
from exper.serializers import DigitalTwinSerializer
from .tasks import run_digital_twin
from urllib.parse import parse_qs
from collections import OrderedDict
from django.conf import settings
from rest_framework.authtoken.models import Token
import json
import bleach

class APIConsumer(WebsocketConsumer):
    def set_authenticated_user(self, user):
        self.authenticated_user = user

    def connect(self):
        self.user = self.scope['user']
        if not self.user.is_anonymous:
            if self.user.profile.is_mediator():
                org_team = DesignTeam.objects.filter(organization=self.user.profile.organization).first()
                if org_team:
                    session_teams = SessionTeam.objects.filter(team=org_team)
                    a_session = None
                    for session_team in session_teams:
                        if session_team.session.status == Session.RUNNING:
                            a_session = session_team.session
                            break
                    if a_session:
                        self.accept()
                        mediator_channel = 'm_' + str(a_session.id)
                        async_to_sync(self.channel_layer.group_add)(
                            mediator_channel,
                            self.channel_name,
                        )
        else :                    
            params = parse_qs(self.scope['query_string'].decode('utf8'))        
            auth_token = params.get('token', (None,))[0]
            if auth_token:            
                user = Token.objects.get(key=auth_token).user
                if user:
                    if user.profile.is_experimenter():
                        self.set_authenticated_user(user)
                        self.accept()
                        async_to_sync(self.channel_layer.group_add)(
                            'twin',
                            self.channel_name,
                        )
            

    #TODO: get reconnection conditions
    #def disconnect(self, close_code):

    # called when owner of this connection sends something over their websocket
    # these should all be commands in this package
    def receive(self, text_data):
        user = self.authenticated_user

        if not user:
            #TODO: log error here
            return

        text_data_json = json.loads(text_data)
        channel = str(text_data_json['channel'])
        type = str(text_data_json['type'])        

        if user.profile.is_experimenter():
            if channel == "twin":
                if settings.DIGITAL_TWIN_ENABLED:
                    if type == "twin.start":
                        session_id = int(bleach.clean(str(text_data_json['session_id'])))
                        session = Session.objects.filter(id=session_id).first()
                        if session:
                            run_digital_twin.delay(session_id)

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

    def event_info(self, event):
        channel = event['channel']
        type = event['type']
        position = event['position']
        info = event['info'] # event.info
        # send message to websocket
        self.send(text_data=json.dumps({
            'channel': channel,
            'type': type,
            'position': position,
            'info': info,
        }))

    def twin_start(self, event):
        channel = event['channel']
        type = event['type'] # twin.start
        session_id = event['session_id']
        # send message to websocket
        self.send(text_data=json.dumps({
            'channel': channel,
            'type': type,
            'session_id': session_id,
        }))

    def twin_info(self, event):
        channel = event['channel']
        type = event['type']
        info = event['info'] # twin.info
        # send message to websocket
        self.send(text_data=json.dumps({
            'channel': channel,
            'type': type,
            'info': info,
        }))

    def twin_complete(self, event):
        channel = event['channel']
        type = event['type']
        # send message to websocket
        self.send(text_data=json.dumps({
            'channel': channel,
            'type': type,
        }))

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