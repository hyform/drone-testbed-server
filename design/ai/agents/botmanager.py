from .botgrammar import BotGrammar
from .database_helper import DatabaseHelper
from .designerbot import DesignerBotAgent
from .opsbot import OpsBotAgent
from django.db.models import Q
from exper.models import UserPosition, GroupPosition, Session, SessionTeam, Group, Market, User
import json
from repo.models import Vehicle, Plan
import logging
from ai.models import DesignerBot, OpsBot

logger = logging.getLogger(__name__)

# manages all bots for all sessions
class BotManager():

    # dictionary that key bots by session id and origianl user name
    #session_bot_twins = {}


    def __init__(self):
        print("init bot manager")

    def initialize_designer_bot_twins(self, session, channel):
        # get designer bot

        db_query = DesignerBot.objects.filter(Q(session=session))
        print("test design ==========================", len(db_query), session.id)

        if len(db_query) != 2:
            DesignerBot.objects.filter(Q(session=session)).delete()
            
            designer_bot = UserPosition.objects.filter(session=session).filter(position__name="Design Specialist 2").first()
            db_helper = DatabaseHelper(session)
            user_roles = db_helper.get_user_roles()
            user_positions = db_helper.get_user_positions()
            for usr in user_roles:
                others = db_helper.get_others_in_channel(session, channel, usr)
                for other in others:
                    if user_positions[usr].id == designer_bot.id:
                        db = DesignerBot()
                        db.session = session
                        db.bot_user_name = usr
                        db.other_user_name = other
                        db.channel_id = channel.id
                        db.save()
                        print("saved ------------ ", other, usr, user_roles[usr],  user_roles[other])


    def initialize_ops_bot_twins(self, session, channel):
        # get designer bot

        db_query = OpsBot.objects.filter(Q(session=session))
        if len(db_query) != 2:
            OpsBot.objects.filter(Q(session=session)).delete()
            ops_bot = UserPosition.objects.filter(session=session).filter(position__name="Operations Specialist 2").first()
            db_helper = DatabaseHelper(session)
            user_roles = db_helper.get_user_roles()
            user_positions = db_helper.get_user_positions()
            for usr in user_roles:
                others = db_helper.get_others_in_channel(session, channel, usr)
                for other in others:
                    if user_positions[usr].id ==  ops_bot.id:
                        ob = OpsBot()
                        ob.session = session
                        ob.bot_user_name = usr
                        ob.other_user_name = other
                        ob.channel_id = channel.id
                        ob.save()

    def get_session_bot_twins(self, session):
        design_bots = DesignerBot.objects.filter(Q(session=session))
        ops_bots = OpsBot.objects.filter(Q(session=session))
        if len(design_bots) == 2 and len(ops_bots) == 2:
            return [design_bots[0], design_bots[1], ops_bots[0], ops_bots[1]]
        elif len(design_bots) == 2:
            return [design_bots[0], design_bots[1], None, None]
        elif len(ops_bots) == 2:
            return [None, None, ops_bots[0], ops_bots[1]]


    def send_adaptive_chat(self, session, msgs):
        bot_setups = self.get_session_bot_twins(session)
        db_helper = DatabaseHelper(session)
        db_helper.set_user_name(bot_setups[0].bot_user_name)
        db_helper.bot_adaptive(msgs)


    def send_adaptive_command(self, session, bot_id):

        bot_setups = self.get_session_bot_twins(session)
        for i in range(4):
            if bot_setups[i]:
                if bot_setups[i].id == bot_id:

                    # make sure to set as a want command
                    bot_setups[i].command = "want"
                    bot_setups[i].save()


                    if i <= 1:
                        db = DesignerBotAgent()
                        msgs = db.send_to_bot(bot_setups[i].id, 'iterate')
                        self.send_adaptive_chat(session, msgs)
                    else:
                        ob = OpsBotAgent()
                        msgs = ob.send_to_bot(bot_setups[i].id, 'iterate')
                        self.send_adaptive_chat(session, msgs)



    def send_to_bots(self, s, user, channel, session):

        db_helper = DatabaseHelper(session)
        structure_name = session.structure.name
        if "Bot" not in structure_name:
            return []

        bot_responses = {}
        bots = self.get_session_bot_twins(session)

        if bots:
            for i, bot in enumerate(bots):
                if bot:
                    if bot.other_user_name == user and bot.channel_id == channel.id:
                        bot_type = "opsbot"
                        if i <= 1:
                            bot_type = "designbot"
                        bg = BotGrammar(bot_type)
                        res = bg.get_json_of_chat(s)

                        if res is not None:
                            db_helper.submit_data_log2(user, "passed_bot_grammar;" + s)

                            # send a message to the bot
                            msgs = None
                            if bot_type == "designbot":
                                db = DesignerBotAgent()
                                msgs = db.send_to_bot(bot.id, s)
                                print("msgs", msgs)
                            else:
                                ob = OpsBotAgent()
                                msgs = ob.send_to_bot(bot.id, s)
                            # if response, return the message and the user or bot who created it
                            if msgs is not None:
                                bot_responses[bot.bot_user_name] = msgs
                        else:
                            if s.startswith("bot"):
                                bot_responses[bot.bot_user_name] = ["intent not understood"]


        return bot_responses


    @staticmethod
    def set_metrics_From_open(session_id, usr, action):
        logger.debug("set_metrics_From_open, action = " + str(action))
        try:
            logger.debug("set_metrics_From_open, BotManager.session_bot_twins = " + str(BotManager.session_bot_twins))
            for key in BotManager.session_bot_twins:
                logger.debug("set_metrics_From_open, usr = " + str(usr))
                logger.debug("set_metrics_From_open, key = " + str(key))
                if usr in key:
                    if 'Profit' in action:
                        logger.debug("set_metrics_From_open: if 'Profit' in action == true")
                        opsbot = BotManager.session_bot_twins[key]
                        profit = float(action.split("Profit,")[1].split(",")[0])
                        startupcost = float(action.split("StartUpCost,")[1].split(",")[0])
                        no_customers = float(action.split("Number of Deliveries,")[1].split(",")[0])
                        config_json = action.split(";")[2]
                        config_json_fix = config_json.replace("\'","\"").replace("True", "true").replace("False", "false")
                        config = json.dumps(json.loads(config_json_fix)["paths"])
                        json_obj_plan = json.loads(config)
                        plan_str = json.dumps(json_obj_plan)
                        opsbot.profit = profit
                        opsbot.cost = startupcost
                        opsbot.no_customers = no_customers
                        opsbot.config = config
                    else:
                        logger.debug("set_metrics_From_open: if 'Profit' in action == false")
                        designbot = BotManager.session_bot_twins[key]
                        config = action.split(";")[3]
                        vehicle = Vehicle.objects.filter(Q(config=config, session_id=session_id)).first()
                        designbot.range = vehicle.range
                        designbot.capacity = vehicle.payload
                        designbot.cost = vehicle.cost
                        designbot.config = vehicle.config
                        logger.debug("range = " + str(vehicle.range))

        except Exception as e:
            logger.error("exception", e)

        logger.debug("set_metrics_From_open complete")

#    @staticmethod
#    def register_timed_event(session_id, event_str):


#        print("register timed event", session_id, event_str)
        # register bots if needed
#        session = Session.objects.filter(id=session_id).first()
#        db_helper = DatabaseHelper(session)
#        user_roles = db_helper.get_user_roles()
#        for usr in user_roles:
#            if usr == user:
#                others = db_helper.get_others_in_channel(session, channel, usr)
#                for other in others:
#                    other_id = other.split("_")[1]
#                    if str(other_id) == "3" or str(other_id) == "5":            # add other id like 10 12, ect
#                        key = self.get_bot_key2(session, user, other)
#                        if key not in BotManager.session_bot_twins:
#                            if 'Design' in user_roles[usr]:
#                                BotManager.session_bot_twins[key] = DesignerBot(usr, session, db_helper, db_helper.get_users()[usr])
#                            if 'Plan' in user_roles[usr]:
#                                BotManager.session_bot_twins[key] = OpsBot(usr, session, db_helper, db_helper.get_users()[usr])
#        print("number of bots", len(BotManager.session_bot_twins))

#        for key in BotManager.session_bot_twins:
#            bot = BotManager.session_bot_twins[key]
#            BotManager.session_bot_twins[key].receive_message(event_str, bot.channel, bot.user)


    # keys a bot using the session id and user name
    def get_bot_key(self, session, user_name):
        return str(session.id) + "," + user_name

    def get_bot_key2(self, session, user_name, bot_name):
        return str(session.id) + "," + user_name + "," + bot_name
