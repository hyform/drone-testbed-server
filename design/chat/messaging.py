from django.contrib.auth.models import User
from django.db.models import Q, Subquery
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from chat.models import Channel
from exper.models import UserPosition, GroupPosition, Position

def new_vehicle_message(group, session, tag):
    message = "A new drone design has been submitted"
    if tag:
        message = "A new drone design has been submitted named '" + str(tag) + "'"
    if group and session:
        help_channel = Channel.objects.filter(name="Help").first()

        group_positions = GroupPosition.objects.filter(group=group).filter(Q(position__role__name="Designer"))
        positions = Position.objects.filter(id__in=Subquery(group_positions.values('position')))
        user_positions = UserPosition.objects.filter(session=session).filter(position__in=positions)
        users = User.objects.filter(id__in=Subquery(user_positions.values('user')))

        for user in users:
            help_instance = str(help_channel.id) + "_" + str(user.id) + "___" + str(session.id)
            async_to_sync(get_channel_layer().group_send)(
                help_instance,
                {
                    'type': 'system.usermessage',
                    'message': message,
                    'sender': "System",
                    'channel': help_instance
                }
            )

        group_positions = None
        positions = None
        user_positions = None
        users = None

        group_positions = GroupPosition.objects.filter(group=group).filter(Q(position__role__name="OpsPlanner"))
        positions = Position.objects.filter(id__in=Subquery(group_positions.values('position')))
        user_positions = UserPosition.objects.filter(session=session).filter(position__in=positions)
        users = User.objects.filter(id__in=Subquery(user_positions.values('user')))

        for user in users:
            help_instance = str(help_channel.id) + "_" + str(user.id) + "___" + str(session.id)
            async_to_sync(get_channel_layer().group_send)(
                help_instance,
                {
                    'type': 'system.usermessage',
                    'message': message,
                    'sender': "System",
                    'channel': help_instance
                }
            )

def new_plan_message(group, session, tag):
    if group and session:
        help_channel = Channel.objects.filter(name="Help").first()

        group_positions = GroupPosition.objects.filter(group=group).filter(Q(position__role__name="Business") | Q(position__role__name="OpsPlanner"))
        positions = Position.objects.filter(id__in=Subquery(group_positions.values('position')))
        user_positions = UserPosition.objects.filter(session=session).filter(position__in=positions)
        users = User.objects.filter(id__in=Subquery(user_positions.values('user')))

        for user in users:
            help_instance = str(help_channel.id) + "_" + str(user.id) + "___" + str(session.id)
            async_to_sync(get_channel_layer().group_send)(
                help_instance,
                {
                    'type': 'system.usermessage',
                    'message': "A new plan has been submitted named '" + str(tag) + "'",
                    'sender': "System",
                    'channel': help_instance
                }
            )

def bot_adapt_message(group, session, msgs, is_design):
    if session:
        if is_design:
            design_channel = Channel.objects.filter(structure=session.structure).filter(name="Design").first()

            for msg in msgs:
                if "Bot suggestion" in msg:
                        design_channel_instance = str(design_channel.id) + "___" + str(session.id)
                        async_to_sync(get_channel_layer().group_send)(
                            design_channel_instance,
                            {
                                'type': 'chat.message',
                                'message': msg,
                                'sender': "Bot",
                                'channel': design_channel_instance
                            }
                        )

            ops_channel = Channel.objects.filter(structure=session.structure).filter(name="Operations").first()

            for msg in msgs:
                if "Bot suggestion" in msg:
                        ops_channel_instance = str(ops_channel.id) + "___" + str(session.id)
                        async_to_sync(get_channel_layer().group_send)(
                            ops_channel_instance,
                            {
                                'type': 'chat.message',
                                'message': msg,
                                'sender': "Bot",
                                'channel': ops_channel_instance
                            }
                        )
        else:
            ops_channel = Channel.objects.filter(structure=session.structure).filter(name="Operations").first()

            for msg in msgs:
                if "Bot suggestion" in msg:
                        ops_channel_instance = str(ops_channel.id) + "___" + str(session.id)
                        async_to_sync(get_channel_layer().group_send)(
                            ops_channel_instance,
                            {
                                'type': 'chat.message',
                                'message': msg,
                                'sender': "Bot",
                                'channel': ops_channel_instance
                            }
                        )

def new_scenario_message(group, session):
    if group and session:
        help_channel = Channel.objects.filter(name="Help").first()

        group_positions = GroupPosition.objects.filter(group=group).filter(Q(position__role__name="OpsPlanner"))
        positions = Position.objects.filter(id__in=Subquery(group_positions.values('position')))
        user_positions = UserPosition.objects.filter(session=session).filter(position__in=positions)
        users = User.objects.filter(id__in=Subquery(user_positions.values('user')))

        for user in users:
            help_instance = str(help_channel.id) + "_" + str(user.id) + "___" + str(session.id)
            async_to_sync(get_channel_layer().group_send)(
                help_instance,
                {
                    'type': 'system.usermessage',
                    'message': "A new scenario has been submitted",
                    'sender': "System",
                    'channel': help_instance
                }
            )

        group_positions = None
        positions = None
        user_positions = None
        users = None

        group_positions = GroupPosition.objects.filter(group=group).filter(Q(position__role__name="Business"))
        positions = Position.objects.filter(id__in=Subquery(group_positions.values('position')))
        user_positions = UserPosition.objects.filter(session=session).filter(position__in=positions)
        users = User.objects.filter(id__in=Subquery(user_positions.values('user')))

        for user in users:
            help_instance = str(help_channel.id) + "_" + str(user.id) + "___" + str(session.id)
            async_to_sync(get_channel_layer().group_send)(
                help_instance,
                {
                    'type': 'system.usermessage',
                    'message': "A new scenario has been submitted",
                    'sender': "System",
                    'channel': help_instance
                }
            )

def new_precheck_message(user, session, check):
    if user and session:
        help_channel = Channel.objects.filter(name="Help").first()

        help_instance = str(help_channel.id) + "_" + str(user.id) + "___" + str(session.id)
        async_to_sync(get_channel_layer().group_send)(
            help_instance,
            {
                'type': 'user.precheck',
                'message': check,
                'sender': "System",
                'channel': help_instance
            }
        )

def new_postcheck_message(user, session, check):
    if user and session:
        help_channel = Channel.objects.filter(name="Help").first()

        help_instance = str(help_channel.id) + "_" + str(user.id) + "___" + str(session.id)
        async_to_sync(get_channel_layer().group_send)(
            help_instance,
            {
                'type': 'user.postcheck',
                'message': check,
                'sender': "System",
                'channel': help_instance
            }
        )
