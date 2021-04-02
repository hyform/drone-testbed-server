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

def twin_info_message(session_id, info):
    async_to_sync(get_channel_layer().group_send)(
    #get_channel_layer().group_send(
        "twin",
        {
            'channel': 'twin',
            'type': 'twin.info',
            'session_id': session_id,
            'info': info,
        }
    )

def twin_pref_message(session_id, info):
    async_to_sync(get_channel_layer().group_send)(
    #get_channel_layer().group_send(
        "twin",
        {
            'channel': 'twin',
            'type': 'twin.pref',
            'session_id': session_id,
            'info': info,
        }
    )

def twin_log_message(session_id, usr, time, action):
    async_to_sync(get_channel_layer().group_send)(
    #get_channel_layer().group_send(
        "twin",
        {
            'channel': 'twin',
            'type': 'twin.log',
            'session_id': session_id,
            'usr': usr,
            'time': time,
            'action': action,
        }
    )

def twin_complete_message(session_id, info):
    async_to_sync(get_channel_layer().group_send)(
    #get_channel_layer().group_send(
        "twin",
        {
            'channel': 'twin',
            'type': 'twin.complete',
            'info': info,
            'session_id': session_id,
        }
    )
