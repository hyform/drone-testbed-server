# chat/consumers.py
from asgiref.sync import async_to_sync
from django.db.models import Q
from channels.generic.websocket import WebsocketConsumer
from django.contrib.auth.models import User
from .models import ChannelPosition, Message, Channel
from exper.models import SessionTeam, UserPosition, Session, UserChecklist
from repo.models import DataLog, DesignTeam, Profile, ExperOrg
from urllib.parse import parse_qs
from collections import OrderedDict
import json
import bleach
from ai.seqtosql.dronebotseqtosql import DroneBotSeqToSQL
from .chat_consumer_listener import ChatConsumerListener
from rest_framework.authtoken.models import Token
from django.conf import settings
from api.tasks import run_digital_twin
from api.models import SessionTimer
from datetime import datetime, timezone

# Websocket for Experimenters in an organization
class OrganizationConsumer(WebsocketConsumer):
    def connect(self):
        self.user = self.scope['user']
        if self.user.profile.is_experimenter():
            self.accept()
            experOrg = ExperOrg.objects.filter(user=self.user).first() #TODO: finalize decision on experimenter in different orgs
            if experOrg:
                help_channel = Channel.objects.filter(name="Help").first()
                channel_instance = str(help_channel.id) + "_organization_" + str(experOrg.organization.id)
                async_to_sync(self.channel_layer.group_add)(
                    channel_instance,
                    self.channel_name,
                )

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

    # receive message from room group
    def system_command(self, event):
        self.message_template(event)


class ChatConsumer(WebsocketConsumer):
    def set_authenticated_user(self, user):
        self.authenticated_user = user

    def connect(self):
        self.authenticated_user = None
        self.user = self.scope['user']
        self.userid = self.scope['user'].id
        self.username = self.scope['user'].username
        self.channels = OrderedDict([])
        st = None

        if self.user.is_anonymous:
            # Connection with auth token
            # Should only be Digital Twin right now
            params = parse_qs(self.scope['query_string'].decode('utf8'))        
            auth_token = params.get('token', (None,))[0]
            if auth_token:            
                user = Token.objects.get(key=auth_token).user
                if user:
                    if user.profile.is_experimenter():
                        self.set_authenticated_user(user)
                        self.accept()
                        # Use simple twin channel for now
                        # TODO: expand this somehow with session and additional instance or something
                        # to allow multiple runs
                        async_to_sync(self.channel_layer.group_add)(
                            'twin',
                            self.channel_name,
                        )
        elif self.user.profile.is_experimenter():
            params = parse_qs(self.scope['query_string'].decode('utf8'))
            teamId = params.get('teamId', (None,))[0]
            team = DesignTeam.objects.filter(id=teamId).first()
            if team:
                self.accept()
                help_channel = Channel.objects.filter(name="Help").first()
                st = SessionTeam.objects.filter(Q(session__status__in=Session.ACTIVE_STATES)&Q(team=team)).first()
                if st:
                    user_profiles = Profile.objects.filter(team=team)
                    for user_profile in user_profiles:
                        if not user_profile.is_experimenter():
                            team_user = user_profile.user
                            up = UserPosition.objects.filter(Q(user=team_user)&Q(session=st.session)).first()
                            if up:
                                precheck = False
                                postcheck = False
                                user_checklist = UserChecklist.objects.filter(session=st.session.id).filter(user=team_user).first()
                                if user_checklist:
                                    precheck = user_checklist.precheck
                                    postcheck = user_checklist.postcheck
                                info_message = up.position.name + "@#@" + str(precheck) + "@#@" + str(postcheck)

                                channel_instance = str(help_channel.id) + "_" + str(team_user.id) + "___" + str(st.session.id)
                                self.channels[channel_instance] = help_channel
                                async_to_sync(self.channel_layer.group_add)(
                                    channel_instance,
                                    self.channel_name,
                                )
                                self.send(text_data=json.dumps({
                                    'type' : 'chat.info',
                                    'message' : info_message,
                                    'sender' : "System",
                                    'channel' : channel_instance
                                }))
                                # Send message over help channel that user has connected
                                async_to_sync(self.channel_layer.group_send)(
                                channel_instance,
                                {
                                    'type': 'session.request',
                                    'message': "respond",
                                    'sender': "Experimenter",
                                    'channel': channel_instance
                                })
                    # Don't include Setup channel for now
                    #setup_channel = Channel.objects.filter(name="Setup").first()
                    #if setup_channel:
                    #    setup_instance = str(setup_channel.id) + "___" + str(st.session.id)
                    #    self.channels[setup_instance] = setup_channel
                    #    async_to_sync(self.channel_layer.group_add)(
                    #        setup_instance,
                    #        self.channel_name,
                    #    )
                    #    self.send(text_data=json.dumps({
                    #        'type' : 'chat.info',
                    #        'message' : "Setup",
                    #        'sender' : "System",
                    #        'channel' : setup_instance
                    #    }))

                    session_channel = Channel.objects.filter(name="Session").first()
                    if session_channel:
                        session_instance = str(session_channel.id) + "___" + str(st.session.id)
                        self.channels[session_instance] = session_channel
                        async_to_sync(self.channel_layer.group_add)(
                            session_instance,
                            self.channel_name,
                        )

                        if st.session.status == Session.RUNNING:
                            running_timer = SessionTimer.objects.filter(session=st.session).filter(timer_type=SessionTimer.RUNNING_START).first()
                            elapsed_seconds = 0
                            if running_timer:
                                current_time = datetime.now(timezone.utc)
                                running_timestamp = running_timer.timestamp
                                if running_timestamp:
                                    time_difference = current_time - running_timestamp
                                    elapsed_seconds = round(time_difference.total_seconds())

                            self.send(text_data=json.dumps({
                                'type' : 'session.time',
                                'message' : str(elapsed_seconds),
                                'sender' : "System",
                                'channel' : session_instance
                            }))
                        self.send(text_data=json.dumps({
                            'type' : 'chat.info',
                            'message' : "Session",
                            'sender' : "System",
                            'channel' : session_instance
                        }))
                        self.send(text_data=json.dumps({
                            'type' : 'system.command',
                            'message' : "init",
                            'sender' : "System",
                            'channel' : session_instance
                        }))
        #TODO: this should go away
        elif self.user.profile.is_mediator():
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
                    channels = Channel.objects.filter(structure=a_session.structure)
                    for channel in channels:
                        channel_instance = str(channel.id) + "___" + str(a_session.id)
                        self.channels[channel_instance] = channel
                    if self.channels:
                        for instance in self.channels:
                            orig_channel = self.channels[instance]
                            async_to_sync(self.channel_layer.group_add)(
                                instance,
                                self.channel_name,
                            )
                            self.send(text_data=json.dumps({
                                'type' : 'chat.info',
                                'message' : orig_channel.name,
                                'sender' : "System",
                                'channel' : instance
                            }))
                        session_channel = Channel.objects.filter(name="Session").first()
                        if session_channel:
                            session_instance = str(session_channel.id) + "___" + str(a_session.id)
                            if session_instance:
                                self.channels[session_instance] = session_channel
                                self.send(text_data=json.dumps({
                                    'type' : 'system.command',
                                    'message' : "init",
                                    'sender' : "System",
                                    'channel' : session_instance
                                }))
        else:
            st = SessionTeam.objects.filter(Q(session__status__in=Session.ACTIVE_STATES)&Q(team=self.user.profile.team)).first()
            if st:
                help_channel = Channel.objects.filter(name="Help").first()
                help_instance = str(help_channel.id) + "_" + str(self.user.id) + "___" + str(st.session.id)
                up = UserPosition.objects.filter(Q(user=self.user)&Q(session=st.session)).first()
                if st.session.status == Session.RUNNING:
                    channel_positions = ChannelPosition.objects.filter(position=up.position)
                    user_channels = Channel.objects.filter(id__in=channel_positions.values('channel'))
                    for channel in user_channels:
                        channel_instance = str(channel.id) + "___" + str(st.session.id)
                        self.channels[channel_instance] = channel
                    self.channels[help_instance] = help_channel
                elif st.session.status == Session.SETUP:
                    #TODO: possibly add org level setting for including setup chat
                    #setup_channel = Channel.objects.filter(name="Setup").first()
                    #setup_instance = str(setup_channel.id) + "___" + str(st.session.id)
                    #self.channels[setup_instance] = setup_channel
                    self.channels[help_instance] = help_channel
                else:
                    self.channels[help_instance] = help_channel
                session_channel = Channel.objects.filter(name="Session").first()
                if session_channel:
                    session_instance = str(session_channel.id) + "___" + str(st.session.id)
                    self.channels[session_instance] = session_channel
                dronebot_channel = Channel.objects.filter(name="DroneBot").first()
                show_dronebot = st.session.structure.name == "Extra"
                if dronebot_channel and show_dronebot:
                    dronebot_instance = str(dronebot_channel.id) + "_" + str(self.user.id) + "___" + str(st.session.id)
                    self.channels[dronebot_instance] = dronebot_channel

                self.accept()

                if up.position.role.name == "Process":
                    mediator_channel = 'm_' + str(st.session.id)
                    async_to_sync(self.channel_layer.group_add)(
                        mediator_channel,
                        self.channel_name,
                    )
                if self.channels:
                    for instance in self.channels:
                        orig_channel = self.channels[instance]
                        async_to_sync(self.channel_layer.group_add)(
                            instance,
                            self.channel_name,
                        )
                        self.send(text_data=json.dumps({
                            'type' : 'chat.info',
                            'message' : orig_channel.name,
                            'sender' : "System",
                            'channel' : instance
                        }))
                    self.send(text_data=json.dumps({
                        'type' : 'system.command',
                        'message' : "init",
                        'sender' : "System",
                        'channel' : session_instance
                    }))
                    # Send message over help channel that user has connected
                    if help_instance:
                        async_to_sync(self.channel_layer.group_send)(
                        help_instance,
                        {
                            'type': 'session.response',
                            'message': "connected",
                            'sender': up.position.name,
                            'channel': help_instance
                        })
        if st:
            # Send out the old messages to this user
            chat_logs = DataLog.objects.filter(session=st.session).filter(Q(type__startswith="chat: ") | Q(type__startswith="intervention: ")).order_by('time')
            for chat_log in chat_logs:
                sender_name = ""
                senderPosition = UserPosition.objects.filter(session=st.session).filter(user=chat_log.user).first()
                if senderPosition:
                    sender_name = senderPosition.position.name
                else:
                    if(chat_log.type.startswith("intervention: ")):
                        sender_name = "Process Manager"
                    else :
                        sender_name = "Experimenter"
                channel_parse = chat_log.type.split('@')
                if len(channel_parse) > 1:
                    channel_instance = channel_parse[len(channel_parse) - 1]
                    self.send(text_data=json.dumps({
                        'type' : 'chat.message',
                        'message' : chat_log.action,
                        'sender' : sender_name,
                        'channel' : channel_instance
                    }))

    def disconnect(self, close_code):
        if self.authenticated_user:
            user = self.authenticated_user
        else:
            user = self.scope["user"]
        # TODO: make sure Experimenter's channels are correctly disconnected

        # leave all of the groups
        st = SessionTeam.objects.filter(Q(session__status__in=Session.ACTIVE_STATES)&Q(team=user.profile.team)).first()
        if st:
            up = UserPosition.objects.filter(Q(user=self.user)&Q(session=st.session)).first()
            #session_channel = Channel.objects.filter(name="Session").first()
            #session_instance = str(session_channel.id) + "___" + str(st.session.id)
            help_channel = Channel.objects.filter(name="Help").first()
            help_instance = str(help_channel.id) + "_" + str(self.user.id) + "___" + str(st.session.id)
            # Send message over help channel that user has disconnected
            async_to_sync(self.channel_layer.group_send)(
            help_instance,
            {
                'type': 'session.response',
                'message': "disconnected",
                'sender': up.position.name,
                'channel': help_instance
            })
        if self.channels:
            for instance in self.channels:
                async_to_sync(self.channel_layer.group_discard)(
                    instance,
                    self.channel_name,
                )

    # receive message from websocket
    def receive(self, text_data):
        if self.authenticated_user:
            user = self.authenticated_user
        else:
            user = self.scope["user"]

        text_data_json = json.loads(text_data)
        message_type = str(text_data_json['type'])
        channel_id = str(text_data_json['channel'])

        # TODO: Hack to integrate api messages which don't have these values right now
        if channel_id != "twin" and message_type != "event.info":
            message = bleach.clean(text_data_json['message'])
            sender_string = self.username        

        if user.profile.is_experimenter():
            if channel_id == "twin":
                if settings.DIGITAL_TWIN_ENABLED:
                    if message_type == "twin.start":
                        session_id = int(bleach.clean(str(text_data_json['session_id'])))
                        session = Session.objects.filter(id=session_id).first()
                        if session:
                            run_digital_twin.delay(session_id)
                return

            # Experimenter, so all channels are user help channels, plus Setup and Session
            channel_position = str(text_data_json['channel_position'])
            channel_team_id = str(text_data_json['channel_team_id'])
            team = DesignTeam.objects.filter(id=channel_team_id).first()
            if team:
                session_team = SessionTeam.objects.filter(Q(session__status__in=Session.ACTIVE_STATES)&Q(team=team)).first()
                if session_team:
                    session = session_team.session
                    if channel_position == "Setup":
                        setup_instance = channel_id
                        setup_channel = Channel.objects.filter(name="Setup").first()
                        Message.objects.create(sender=user, channel=setup_channel, message=message, session=session)
                        DataLog.objects.create(user=user, session=session, action=message, type='chat: ' + channel_position + ' @' + setup_instance)
                        # send message to room group
                        async_to_sync(self.channel_layer.group_send)(
                            setup_instance,
                            {
                                'type': 'chat.message',
                                'message': message,
                                'sender': "Experimenter",
                                'channel': setup_instance
                            }
                        )
                    elif channel_position == "Session":
                        session_instance = channel_id
                        session_channel = Channel.objects.filter(name="Session").first()
                        Message.objects.create(sender=user, channel=session_channel, message=message, session=session)
                        DataLog.objects.create(user=user, session=session, action=message, type='chat: ' + channel_position + ' @' + session_instance)
                        # send message to room group
                        async_to_sync(self.channel_layer.group_send)(
                            session_instance,
                            {
                                'type': 'chat.message',
                                'message': message,
                                'sender': "Experimenter",
                                'channel': session_instance
                            }
                        )
                    else: #Help Channel of a user
                        channel_user = None
                        user_positions = UserPosition.objects.filter(Q(session=session)&Q(position__name=channel_position))
                        for user_position in user_positions:
                            user_profile = Profile.objects.filter(team=team).filter(user=user_position.user).first()
                            if user_profile:
                                channel_user = user_profile.user
                                channel_instance = channel_id
                                help_channel = Channel.objects.filter(name="Help").first()
                                Message.objects.create(sender=user, channel=help_channel, message=message, session=session)
                                DataLog.objects.create(user=user, session=session, action=message, type='chat: ' + channel_position + ' @' + channel_instance)
                                # send message to room group
                                async_to_sync(self.channel_layer.group_send)(
                                    channel_instance,
                                    {
                                        'type': 'chat.message',
                                        'message': message,
                                        'sender': "Experimenter",
                                        'channel': channel_instance
                                    }
                                )
        else:
            # Non-Experimenter, so all channels are their own
            st = SessionTeam.objects.filter(Q(session__status__in=Session.ACTIVE_STATES)&Q(team=user.profile.team)).first()
            user_position = UserPosition.objects.filter(Q(session__status__in=Session.ACTIVE_STATES)&Q(user=user)).first()
            if user_position:
                position = user_position.position
                if position:
                    sender_string = position.name

            channel_user_id = str(self.user.id)
            channel_real_id = channel_id.split("_")[0]
            channel = Channel.objects.get(id=channel_real_id)
            channel_instance = channel_id

            if message_type == "session.response":
                async_to_sync(self.channel_layer.group_send)(
                    channel_instance,
                    {
                        'type': 'session.response',
                        'message': message,
                        'sender': sender_string,
                        'channel': channel_instance
                    }
                )
            else:
                Message.objects.create(sender=user, channel=channel, message=message, session=st.session)
                DataLog.objects.create(user=user, session=st.session, action=message, type='chat: ' + channel.name + ' @' + channel_instance)

                async_to_sync(self.channel_layer.group_send)(
                    channel_instance,
                    {
                        'type': 'chat.message',
                        'message': message,
                        'sender': sender_string,
                        'channel': channel_instance
                    }
                )

            if channel.name == "DroneBot":

                self.send(text_data=json.dumps({
                    'type' : 'system.usermessage',
                    'message' : "I am working on your request ...",
                    'sender' : "DroneBot",
                    'channel' : channel_instance
                }))


                html_display = '<br>Select a preferred design(s) to save into your session ...<br><br>'
                vehicles, msg = DroneBotSeqToSQL.run(message, user, st.session)
                if len(vehicles) > 0:
                    counter = 0
                    for v in vehicles:
                        counter += 1
                        scale_cost = 1
                        if st.session.market.name == 'Market 2':
                            scale_cost = 0.7
                        html_display += "<button onclick=\"savevehicle('" + str(v[4]) + "', " + str(v[0]) + "," + str(v[2]) + "," + str(v[1]) + "," + str(v[3]) + ")\">Design " + str(counter) + "</button> <b>range(mi)</b>=" + str(round(v[0], 2)) + " , "
                        html_display += "<b>capacity(lb)</b>=" + str(round(v[2], 0)) + " , "
                        html_display += "<b>cost($)</b>=" + str(round(scale_cost*float(v[1]), 0)) + "<br><br>"

                else:
                    html_display = "<br>" + msg + "<br>"
                async_to_sync(self.channel_layer.group_send)(
                    channel_instance,
                    {
                        'type': 'system.usermessage',
                        'message': html_display,
                        'sender': "DroneBot",
                        'channel': channel_instance
                    }
                )

            #ChatConsumerListener.team.register_chat(message, channel_real_id)


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
    # Note Channels transforms types aaa.bbb to aaa_bbb defined below
        
    # receive message from room group
    def chat_message(self, event):
        self.message_template(event)

    # request that users in session chat respond
    def session_request(self, event):
        self.message_template(event)

    # a response to a user request in session channel
    # also sent on session channel when connecting
    def session_response(self, event):
        self.message_template(event)

    # receive message from room group
    def system_command(self, event):
        self.message_template(event)

    # a system message sent to a specific user
    def system_usermessage(self, event):
        self.message_template(event)

    # a system message sent to a specific user
    def user_precheck(self, event):
        self.message_template(event)

    # a system message sent to a specific user
    def user_postcheck(self, event):
        self.message_template(event)

    # the current time of a session
    def session_time(self, event):
        self.message_template(event)

    def event_info(self, event):
        channel = event['channel']
        type = event['type']
        position = event['position']
        info = event['info'] # event.info
        time = event['time']
        # send message to websocket
        self.send(text_data=json.dumps({
            'channel': channel,
            'type': type,
            'position': position,
            'info': info,
            'time': time,
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
