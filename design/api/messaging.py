from django.contrib.auth.models import User
from django.db.models import Q, Subquery
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from chat.models import Channel
from exper.models import UserPosition, GroupPosition, Position

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