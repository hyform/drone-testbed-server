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
from api.tasks import run_digital_twin, pause_digital_twin, setup_digital_twin, set_digital_twin_preference, set_digital_twin_uncertainty
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

        print("not sure when this is getting used")


#        text_data_json = json.loads(text_data)
#        channel = str(text_data_json['channel'])
#        type = str(text_data_json['type'])

#        if user.profile.is_experimenter():
#            if channel == "twin":
#                if settings.DIGITAL_TWIN_ENABLED:
#                    if type == "twin.start":

                        # default values
#                        unit_structure = 1
#                        market = 1
#                        ai = 1

                        # optional values for now with try and excepts
#                        try:
#                            unit_structure = int(bleach.clean(str(text_data_json['unit_structure'])))
#                        except Exception as e:
#                            print(e)

#                        try:
#                            market = int(bleach.clean(str(text_data_json['market'])))
#                        except Exception as e:
#                            print(e)

#                        try:
#                            ai = int(bleach.clean(str(text_data_json['ai'])))
#                        except Exception as e:
#                            print(e)

#                        user_id = int(bleach.clean(str(user.id)))
#                        setup_digital_twin(user_id, unit_structure, market, ai)


#                    if message_type == "twin.run":
#                        session_id = int(bleach.clean(str(text_data_json['session_id'])))
#                        action_type = bleach.clean(str(text_data_json['action']))

#                        print("action type 2 -------------------------------------------- ", action_type)

                        #if action_type == 'run':
                        #    run_digital_twin.delay(session_id)
                        #elif action_type == 'pause':
                        #    pause_digital_twin.delay(session_id)


#                    if message_type == "twin.pref":
#                        session_id = int(bleach.clean(str(text_data_json['session_id'])))
#                        set_digital_twin_preference.delay(session_id, text_data)


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
        session_id = event['session_id']
        # send message to websocket
        self.send(text_data=json.dumps({
            'channel': channel,
            'type': type,
            'info': info,
            'session_id': session_id,
        }))

    def twin_pref(self, event):
        channel = event['channel']
        type = event['type']
        info = event['info'] # twin.info
        session_id = event['session_id']
        # send message to websocket
        self.send(text_data=json.dumps({
            'channel': channel,
            'type': type,
            'info': info,
            'session_id': session_id,
        }))

    def twin_log(self, event):
        channel = event['channel']
        type = event['type']
        session_id = event['session_id']
        user_name = event['user_name']
        time_min = event['time_min']
        action = event['action']
        # send message to websocket
        self.send(text_data=json.dumps({
            'channel': channel,
            'type': type,
            'session_id': session_id,
            'user_name': user_name,
            'time_min': time_min,
            'action': action,
        }))

    def twin_complete(self, event):
        channel = event['channel']
        type = event['type']
        # send message to websocket
        self.send(text_data=json.dumps({
            'channel': channel,
            'type': type,
        }))
