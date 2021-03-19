from django.db import models
from django.contrib.auth.models import User

from exper.models import Session, Position
from chat.models import Channel

class SessionTimer(models.Model):
    timer_type = models.IntegerField(default=0)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(null=True, blank=True)

    RUNNING_START = 1

class MessageChat(models.Model):
    # Timestamps
    timestamp = models.DateTimeField() # Server time this even is created
    session_timestamp = models.DateTimeField() # Time since most recent session start that this event is created

    # Channel
    channel = models.ForeignKey(Channel, null=True, on_delete=models.SET_NULL)
    channelId = models.CharField(max_length=255, null=True)

    # Type
    message_type = models.CharField(max_length=255, null=True)

    # Sender
    position = models.ForeignKey(Position, null=True, on_delete=models.SET_NULL)
    from_experimenter = models.BooleanField(default=False)
    from_system = models.BooleanField(default=False)

    # Message
    message = models.CharField(max_length=2048, null=True)

    