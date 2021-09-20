from .botgrammar import BotGrammar
from .database_helper import DatabaseHelper
from .designerbot import DesignerBot
from .opsbot import OpsBot

# manages all bots for all sessions
class BotManager():

    # dictionary that key bots by session id and origianl user name
    session_bot_twins = {}


    def __init__(self):
        print("init bot manager")

    # register as a bot if not already, assign its session and db_helper (for easier design or plan submission)
    def register_session_bot(self, session, name, channel):
        db_helper = DatabaseHelper(session)
        user_roles = db_helper.get_user_roles()
        for usr in user_roles:
            if usr == name:

                db_helper = DatabaseHelper(session)
                others = db_helper.get_others_in_channel(session, channel, usr)

                for other in others:
                    key = self.get_bot_key2(session, other, usr)
                    if key not in BotManager.session_bot_twins:
                        if 'Design' in user_roles[usr]:
                            BotManager.session_bot_twins[key] = DesignerBot(usr, session, db_helper, db_helper.get_users()[usr])
                            BotManager.session_bot_twins[key].set_channel(channel)
                        if 'Plan' in user_roles[usr]:
                            BotManager.session_bot_twins[key] = OpsBot(usr, session, db_helper, db_helper.get_users()[usr])
                            BotManager.session_bot_twins[key].set_channel(channel)



                #key = self.get_bot_key(session, usr)
                #if key not in BotManager.session_bot_twins:
                #    if 'Design' in user_roles[usr]:
                #        BotManager.session_bot_twins[key] = DesignerBot(usr, session, db_helper, db_helper.get_users()[usr])
                #    if 'Plan' in user_roles[usr]:
                #        BotManager.session_bot_twins[key] = OpsBot(usr, session, db_helper, db_helper.get_users()[usr])


    # test a channel chat message to find a listening bot
####    def test_grammar_and_distribute(self, s, user, channel, session, channel_instance, channel_layer):
    def test_grammar_and_distribute(self, s, user, channel, session):

        bot_responses = {}

        db_helper = DatabaseHelper(session)
        others = db_helper.get_others_in_channel(session, channel, user)

        # send message to other bots
        for other in others:

            # check for a bot key
            #key = self.get_bot_key(session, other)
            key = self.get_bot_key2(session, user, other)

            # is this a bot
            if key in BotManager.session_bot_twins:

                bot_type = BotManager.session_bot_twins[key].get_type()
                print("bot_type", bot_type)

                bg = BotGrammar(bot_type)
                res = bg.get_json_of_chat(s)

                print("grammamr result", res)


                if res is not None:

                    # send a message to the bot
                    msgs = BotManager.session_bot_twins[key].receive_message(s, channel, user)

                    # if response, return the message and the user or bot who created it
                    if msgs is not None:
                        bot_responses[db_helper.get_users()[other]] = msgs

                else:
                    if "bot" in s:
                        bot_responses[db_helper.get_users()[other]] = ["intent not understood"]


        return bot_responses


    def send_to_bots(self, s, user, channel, session):

        structure_name = session.structure.name
        if "Bot" not in structure_name:
            return []

        # register bots if needed
        db_helper = DatabaseHelper(session)
        user_roles = db_helper.get_user_roles()
        for usr in user_roles:
            if usr == user:
                others = db_helper.get_others_in_channel(session, channel, usr)
                for other in others:
                    other_id = other.split("_")[1]
                    key = self.get_bot_key2(session, user, other)
                    if key not in BotManager.session_bot_twins:
                        if 'Design' in user_roles[usr]:
                            BotManager.session_bot_twins[key] = DesignerBot(usr, session, db_helper, db_helper.get_users()[usr])
                            BotManager.session_bot_twins[key].set_channel(channel)
                        if 'Plan' in user_roles[usr]:
                            BotManager.session_bot_twins[key] = OpsBot(usr, session, db_helper, db_helper.get_users()[usr])
                            BotManager.session_bot_twins[key].set_channel(channel)

        # get responses
        bot_responses = {}
        others = db_helper.get_others_in_channel(session, channel, user)

        # send message to other bots
        for other in others:

            # check for a bot key
            #key = self.get_bot_key(session, other)
            key = self.get_bot_key2(session, user, other)

            # is this a bot
            if key in BotManager.session_bot_twins:

                bot_type = BotManager.session_bot_twins[key].get_type()
                bg = BotGrammar(bot_type)
                res = bg.get_json_of_chat(s)
                if res is not None:

                    # send a message to the bot
                    msgs = BotManager.session_bot_twins[key].receive_message(s, channel, user)

                    # if response, return the message and the user or bot who created it
                    if msgs is not None:
                        bot_responses[db_helper.get_users()[other]] = msgs
                else:
                    if "bot" in s:
                        bot_responses[db_helper.get_users()[other]] = ["intent not understood"]

        return bot_responses

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