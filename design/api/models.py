from django.db import models
from django.contrib.auth.models import User

from exper.models import Group, Session, Position, Organization, Study, Experiment
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
    message = models.TextField(null=True, blank=True)

'''
# ------ Vehicles --------
class Vehicle(models.Model):
    config = models.TextField()

#TODO: ai_designer isn't correct yet. need to think some more on this one

class VehicleEvaluation(models.Model):
    config = models.ForeignKey(Vehicle, null=True, on_delete=models.SET_NULL) 
    range = models.FloatField()
    velocity = models.FloatField()
    cost = models.FloatField()
    payload = models.FloatField()
    ai_designer = models.BooleanField(default=False)

class VehicleSessionEvaluation(models.Model):
    session = models.ForeignKey(Session, default=None, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, default=None, on_delete=models.CASCADE)    
    tag = models.CharField(max_length=255)    
    result = models.CharField(max_length=100)
    evaluation = models.ForeignKey(VehicleEvaluation, null=True, on_delete=models.SET_NULL)

# ------- Customers/Warehouse ---------------

# ------- Plans/Scenarios ----------------
'''