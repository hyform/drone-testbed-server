from django.db import models
from django.contrib.auth.models import User
from repo.models import DesignTeam
from exper.models import Structure, Position, Session

# Create your models here.


class Channel(models.Model):
    name = models.CharField(max_length=25)
    structure = models.ForeignKey(Structure, null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        if self.structure:
            return self.name + '_' + self.structure.name
        else:
            return self.name + '_None'

class ChannelPosition(models.Model):
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)

    def __str__(self):
        if self.position:
            return self.channel.name + '_' + self.position.name
        else:
            return self.channel.name + '_None'

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now=True)
    
