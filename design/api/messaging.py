from django.contrib.auth.models import User
from django.db.models import Q, Subquery
from asgiref.sync import async_to_sync

from channels.layers import get_channel_layer

def event_info_message(channel, position, info, time):
    async_to_sync(get_channel_layer().group_send)(
        channel,
        {
            'channel': channel,
            'type': 'event.info',
            'position': position,
            'info': info,
            'time': time,
        }
    )

def twin_info_message(info):
    async_to_sync(get_channel_layer().group_send)(
    #get_channel_layer().group_send(
        "twin",
        {
            'channel': 'twin',
            'type': 'twin.info',
            'info': info,
        }
    )

def twin_complete_message(info):
    async_to_sync(get_channel_layer().group_send)(
    #get_channel_layer().group_send(
        "twin",
        {
            'channel': 'twin',
            'type': 'twin.complete',
            'info': info,
        }
    )
