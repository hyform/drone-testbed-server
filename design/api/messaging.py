from django.contrib.auth.models import User
from django.db.models import Q, Subquery
from asgiref.sync import async_to_sync

from channels.layers import get_channel_layer

def get_event_channel(session_id):
    event_channel = "session_event" + "__" + str(session_id)

def session_start_message(session_id, time):
    channel = get_event_channel(session_id)
    async_to_sync(get_channel_layer().group_send)(
        channel,
        {
            'channel': channel,
            'type': 'session.start',
            'time': time,
        }
    )

def session_stop_message(session_id, time):
    channel = get_event_channel(session_id)
    async_to_sync(get_channel_layer().group_send)(
        channel,
        {
            'channel': channel,
            'type': 'session.stop',
            'time': time,
        }
    )

# Process Manager
# TODO: migrate this to new events

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

# Digital Twin
# TODO: move this to a Twin app

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

def twin_uncertainty_message(session_id, info):
    async_to_sync(get_channel_layer().group_send)(
    #get_channel_layer().group_send(
        "twin",
        {
            'channel': 'twin',
            'type': 'twin.uncertainty',
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
