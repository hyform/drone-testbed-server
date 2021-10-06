from asgiref.sync import async_to_sync

from .botgrammar import BotGrammar
from .adaptive_team_ai_updated_planner import AdaptiveTeamAIUpdatedPlanner

from django.db.models import Q

from chat.models import ChannelPosition, Message, Channel
from exper.models import SessionTeam, UserPosition, Session, UserChecklist
from repo.models import DataLog, DesignTeam, Profile, ExperOrg

from process.messaging import send_bot_helper

import time

from api.models import SessionTimer
from datetime import datetime, timedelta, timezone


# parent class of all bots
class AiBot():

    def __init__(self, name, session, db_helper, user):
        self.session = session
        self.db_helper = db_helper
        self.name = name
        self.user= user
        self.channel = None

        self.SEND = "send"
        self.RECEIVE = "receive"

        self.adapt = True

        self.saved_states = {}

        running_timer = SessionTimer.objects.filter(session=self.session).filter(timer_type=SessionTimer.RUNNING_START).first()
        elapsed_seconds = -1
        if running_timer:
            current_time = datetime.now(timezone.utc)
            running_timestamp = running_timer.timestamp
            if running_timestamp:
                time_difference = current_time - running_timestamp
                elapsed_seconds = round(time_difference.total_seconds())
        else:
            elapsed_seconds = 0

        self.ITERATION_INTERVAL = 5
        self.iter_Time = self.ITERATION_INTERVAL + elapsed_seconds

        self.reset_preferece()

    def set_channel(self, channel):
        self.channel = channel

    def is_adapt(self):
        return self.adapt

    def set_time(self, time_experiment, to_user):
        if time_experiment >= self.iter_Time*60:
            self.iter_Time += self.ITERATION_INTERVAL
            if self.command is None:
                res = self.adapt_function("iterate")
            else:
                res = self.receive_message("iterate", self.channel, self.user)
            print(res)
            for r in res:
                send_bot_helper(self.user, self.channel, self.session, '@'  + to_user + " " + r)


    def reset_preferece(self):
        self.command = None
        self.command_type = None
        self.referenced_obj = None
        self.variable_info = []
        self.response = []

    def adaptive_reset_preferece(self):
        self.command = None
        self.command_type = None
        self.response = []

    def get_type(self):
        return "aibot"

    # receives a message from a channel to process it an assign grammar based information variables
    def receive_message(self, s, channel, usr):


        print("-------------- received")

        # reset preference
        if not self.adapt:
            self.reset_preferece()
        else:
            self.adaptive_reset_preferece()

        # get type
        bot_type = self.get_type()

        # parse chat, better way ?
        bg = BotGrammar(bot_type)
        json_chat = bg.get_json_of_chat(s)

        if json_chat == "no":
            self.command = "no"
            return

        if 'want' in json_chat['type'] or 'working' in json_chat['type'] :
            conds = json_chat['conditions']
            print("conds", conds)
            for cond in conds:
                if 'type' in cond:
                    if 'reference' in cond['type']:
                        self.referenced_obj = cond['name']
                    elif 'want_cond' in cond['type']:
                        var_info = VariableInformation()
                        if 'PREFDIR' in cond:
                            var_info.pref_dir = cond['PREFDIR']
                        if 'VARIABLE' in cond:
                            var_info.variable = cond['VARIABLE']
                        if 'SIGNED_NUMBER' in cond:
                            var_info.value = float(cond['SIGNED_NUMBER'])
                        self.variable_info.append(var_info)
        if 'want' in json_chat['type']:
            self.command = "want"
        if 'working' in json_chat['type']:
            self.command = "working"

        if 'ping' in json_chat['type']:
            self.command = "ping"
            if 'ping_status' in json_chat['type']:
                self.command_type = "status"
            if 'ping_start' in json_chat['type']:
                self.command_type = "start"
            if 'ping_var' in json_chat['type']:
                self.command_type = "state"
                if 'variable' in json_chat:
                    var_info = VariableInformation()
                    var_info.variable = json_chat['variable']
                    self.variable_info.append(var_info)
            if 'ping_satisfied' in json_chat['type']:
                self.command_type = "satisfied"
                conds = json_chat['conditions']
                for cond in conds:
                    if 'reference' in cond['type']:
                        self.referenced_obj = cond['name']
            if 'ping_unsatisfied' in json_chat['type']:
                if 'variable' in json_chat:
                    self.command_type = "unsatisfied"
                    var_info = VariableInformation()
                    var_info.variable = json_chat['variable']
                    self.variable_info.append(var_info)
            if 'ping_response' in json_chat['type']:
                self.command_type = "response"
                var_info = VariableInformation()
                if 'VARIABLE' in json_chat:
                    var_info.variable = json_chat['VARIABLE']
                if 'SIGNED_NUMBER' in json_chat:
                    var_info.value = float(json_chat['SIGNED_NUMBER'])
                self.variable_info.append(var_info)


####    def restart_queue(self, t):
####        self.queue_time = t
####        while self.queue_time > 0:
####            time.sleep(1)
####            self.queue_time -= 1
####        response_copy = []
####        for msg in self.response:
####            response_copy.append(msg)
####        self.response = []
####        for msg in response_copy:
####            self.send_msg(msg)
####            if "ping satisfied" in msg:
####                self.save_cache()


####    def send_msg(self, msg):
####        st = SessionTeam.objects.filter(Q(session__status__in=Session.ACTIVE_STATES)&Q(team=self.user.profile.team)).first()
####        user_position = UserPosition.objects.filter(Q(session__status__in=Session.ACTIVE_STATES)&Q(user=self.user)).first()
####        if user_position:
####            position = user_position.position
####            if position:
####                sender_string = position.name
####                Message.objects.create(sender=self.user, channel=self.channel, message=msg, session=st.session)
####                DataLog.objects.create(user=self.user, session=st.session, action=msg, type='chat: ' + self.channel.name + ' @' + self.channel_instance)

                # get the position name of the bot
####                async_to_sync(self.channel_layer.group_send)(
####                    self.channel_instance,
####                    {
####                        'type': 'chat.message',
####                        'message': msg,
####                        'sender': sender_string,
####                        'channel': self.channel_instance
####                    }
####                )


# class to store want information specific to variables
class VariableInformation():

    def __init__(self):
        self.pref_dir = None
        self.variable = None
        self.value = float("nan")
