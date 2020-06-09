from django.db import models
from django.contrib.auth.models import User

#from repo.models import DesignTeam

# Create your models here.

class Market(models.Model):
    name = models.CharField(max_length=50)
    def __str__(self):
        return self.name

class Study(models.Model):
    name = models.CharField(max_length=100)
    purpose = models.TextField()
    lead = models.CharField(max_length=50, default='no one')
    def __str__(self):
        return self.name

class Experiment(models.Model):
    name = models.CharField(max_length=100)
    study = models.ForeignKey( Study, on_delete=models.CASCADE)
    user = models.ForeignKey( User, null=True, on_delete=models.CASCADE)
    def __str__(self):
        return self.name

class Structure(models.Model):
    name = models.CharField(max_length=25)
    def __str__(self):
        return self.name
    
class Role(models.Model):
    name = models.CharField(max_length=50)
    def __str__(self):
        return self.name
    
class Position(models.Model):
    name = models.CharField(max_length=50)
    structure = models.ForeignKey(Structure, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    def __str__(self):
        return self.name + '_' + self.structure.name

class Session(models.Model):
    name = models.CharField(max_length=100)
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)
    prior_session = models.ForeignKey('self', blank=True, null=True, on_delete=models.CASCADE)
    structure = models.ForeignKey(Structure, on_delete=models.CASCADE)
    market = models.ForeignKey(Market, on_delete=models.CASCADE)
    use_ai = models.BooleanField()

    NONE = 0
    RUNNING = 1
    TEMPLATE = 2
    PAUSED = 3 # Not used yet
    STOPPED = 4
    ARCHIVED = 5
    SETUP = 6
    PRESESSION = 7
    POSTSESSION = 8
    ACTIVE_STATES = [SETUP, PRESESSION, RUNNING, POSTSESSION]
    status = models.IntegerField(default=STOPPED)

    def __str__(self):
        return self.name

class Group(models.Model):
    name = models.CharField(max_length=50)
    structure = models.ForeignKey(Structure, on_delete=models.CASCADE)
    def __str__(self):
        return self.name+'_'+self.structure.name
    
class GroupPosition(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    primary = models.BooleanField(default=False)
    def __str__(self):
        return self.group.name+'_'+self.position.name+'_'+self.position.structure.name

class SessionTeam(models.Model):
    team = models.ForeignKey('repo.DesignTeam', on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)

class UserPosition(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, null=True, on_delete=models.CASCADE)

class Organization(models.Model):
    name = models.CharField(max_length=50)
    def __str__(self):
        return self.name

class UserChecklist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    precheck = models.BooleanField(default=False)
    postcheck = models.BooleanField(default=False)
