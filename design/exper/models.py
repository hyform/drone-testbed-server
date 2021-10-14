from django.db import models
from django.contrib.auth.models import User

class Organization(models.Model):
    name = models.CharField(max_length=50)
    def __str__(self):
        return self.name

class Market(models.Model):
    name = models.CharField(max_length=50)
    def __str__(self):
        return self.name

class Study(models.Model):
    name = models.CharField(max_length=100)
    purpose = models.TextField()
    lead = models.CharField(max_length=50, default='no one')
    organization = models.ForeignKey(Organization, null=True, blank=True, on_delete=models.SET_NULL)
    def __str__(self):
        return self.name

class Experiment(models.Model):
    name = models.CharField(max_length=100)
    study = models.ForeignKey(Study, on_delete=models.CASCADE)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL) # TODO: Deprecate and delete
    def __str__(self):
        return self.name

class Structure(models.Model):
    name = models.CharField(max_length=25)
    organization = models.ForeignKey(Organization, null=True, on_delete=models.CASCADE)
    def __str__(self):
        return self.name

# TODO: Nothing for this table is implemented yet
# If a structure appears in this table, then it is only available to the Organizations it is linked to in this table
# This will be loose enforcement for now. Basically it only filters out options in session creation
class StructureOrganization(models.Model):
    structure = models.ForeignKey(Structure, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)

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

class Exercise(models.Model):
    name = models.CharField(max_length=250, blank=True)
    experiment = models.ForeignKey(Experiment, null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Session(models.Model):
    name = models.CharField(max_length=100)
    experiment = models.ForeignKey(Experiment, null=True, blank=True, on_delete=models.SET_NULL) #TODO: This needs to be deprecated, then removed
    exercise = models.ForeignKey(Exercise, blank=True, null=True, on_delete=models.CASCADE)
    index = models.IntegerField(default=0)
    prior_session = models.ForeignKey('self', blank=True, null=True, on_delete=models.CASCADE) #TODO: This needs to be deprecated, then removed
    structure = models.ForeignKey(Structure, on_delete=models.CASCADE)
    market = models.ForeignKey(Market, on_delete=models.CASCADE)
    is_tutorial = models.BooleanField(default=False)
    use_ai = models.BooleanField()
    use_process_ai = models.BooleanField(default=False)

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

class UserChecklist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    precheck = models.BooleanField(default=False)
    postcheck = models.BooleanField(default=False)

class CustomLinks(models.Model):
    active = models.BooleanField(default=True)
    text = models.CharField(max_length=255)
    link = models.CharField(max_length=2048)
    SURVEY = 1
    FORM = 2
    BRIEF = 3
    TUTORIAL = 4
    link_type = models.IntegerField(null=True, blank=True)
    org = models.ForeignKey(Organization, null=True, blank=True, on_delete=models.SET_NULL)
    study = models.ForeignKey(Study, null=True, blank=True, on_delete=models.SET_NULL)
    experiment = models.ForeignKey(Experiment, null=True, blank=True, on_delete=models.SET_NULL)
    role = models.ForeignKey(Role, null=True, blank=True, on_delete=models.SET_NULL)
    structure = models.ForeignKey(Structure, null=True, blank=True, on_delete=models.SET_NULL)
    position = models.ForeignKey(Position, null=True, blank=True, on_delete=models.SET_NULL)
    is_team = models.BooleanField(null=True, blank=True)
    ai = models.BooleanField(null=True, blank=True)
    status = models.IntegerField(null=True, blank=True)
    first = models.BooleanField(null=True, blank=True)
    last = models.BooleanField(null=True, blank=True)
    in_tutorial = models.BooleanField(null=True, blank=True)

    # Add Market here
    # Add int here for session position in exercise
    #TODO: add in study and experiment filtering

class DigitalTwin(models.Model):
    user_position = models.ForeignKey(UserPosition, null=True, blank=True, on_delete=models.CASCADE)
    open_time_interval = models.FloatField(default=1.0)
    save_time_interval = models.FloatField(default=2.0)
    quality_bias = models.FloatField(default=0.1)
    self_bias = models.FloatField(default=0.1)
    temperature = models.FloatField(default=0.2)
    satisficing_factor = models.FloatField(default=0.2)

class DigitalTwinRequirement(models.Model):
    digital_twin = models.ForeignKey(DigitalTwin, null=True, blank=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    lower_limit = models.FloatField(default=0.0)
    upper_limit = models.FloatField(default=0.0)

class DigitalTwinPreference(models.Model):
    digital_twin = models.ForeignKey(DigitalTwin, null=True, blank=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    pref_value = models.FloatField(default=0.0)
    pref_type = models.IntegerField(default=0)          # maybe 0 : weighted sums, 1 :goal based
