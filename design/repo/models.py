from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from exper.models import Group, Session, Organization

# Create your models here

class DesignTeam(models.Model):
    name = models.CharField(max_length=50)
    initialscore = models.FloatField(default=0.0)
    currentscore = models.FloatField(default=0.0)
    organization = models.ForeignKey(Organization, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    team = models.ForeignKey(DesignTeam, null=True, blank=True, on_delete=models.SET_NULL)
    is_exper = models.BooleanField(default=False)
    organization = models.ForeignKey(Organization, null=True, blank=True, on_delete=models.SET_NULL)
    temp_code = models.TextField(default="", blank=True)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

class Vehicle(models.Model):
    tag = models.CharField(max_length=100)
    group = models.ForeignKey(Group, default=None, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, default=None, on_delete=models.CASCADE)
    config = models.TextField()
    result = models.CharField(max_length=100)
    range = models.FloatField()
    velocity = models.FloatField()
    cost = models.FloatField()
    payload = models.FloatField()

class Address(models.Model):
    x = models.FloatField()
    z = models.FloatField()
    region = models.CharField(max_length=20)
    def __str__(self):
        return str(self.x)+', '+str(self.z)

class Customer(models.Model):
    market = models.ForeignKey('exper.Market', on_delete=models.CASCADE)
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    payload = models.CharField(max_length=20)
    weight = models.FloatField()

class Warehouse(models.Model):
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, null=True, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, null=True, on_delete=models.CASCADE)

class Scenario(models.Model):
    tag = models.CharField(max_length=100)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    # customers = models.ManyToManyField(Customer, through='CustomerScenario', related_name='customers')
    group = models.ForeignKey(Group, null=True, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, null=True, on_delete=models.CASCADE)
    version = models.IntegerField(default=0)

class CustomerScenario(models.Model):
    scenario = models.ForeignKey(Scenario, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    selected = models.BooleanField(default=True)

class Waypoint(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    deliverytime = models.FloatField()


class Plan(models.Model):
    tag = models.CharField(max_length=100)
    scenario = models.ForeignKey(Scenario, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, null=True, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, null=True, on_delete=models.CASCADE)

class Path(models.Model):
    plan = models.ForeignKey(Plan, related_name='paths', null=True, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    leavetime = models.FloatField(default=0.0)
    returntime = models.FloatField(default=0.0)
    group = models.ForeignKey(Group, null=True, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, null=True, on_delete=models.CASCADE)

class PathCustomer(models.Model):
    path = models.ForeignKey(Path, related_name='customers', on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    stop = models.IntegerField(default=1)

class DataLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, null=True, on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now=True)
    action = models.TextField()
    type = models.CharField(max_length=255, default='client')


class VehicleDemo(models.Model):
    xmlstring = models.TextField()
    tag = models.CharField(max_length=50)
    team = models.CharField(max_length=50)

class ScenarioDemo(models.Model):
    xmlstring = models.TextField()
    tag = models.CharField(max_length=50)
    team = models.CharField(max_length=50)

class OpsPlanDemo(models.Model):
    xmlstring = models.TextField()
    tag = models.CharField(max_length=50)
    team = models.CharField(max_length=50)

class PlayDemo(models.Model):
    xmlstring = models.TextField()
    tag = models.CharField(max_length=50)
    team = models.CharField(max_length=50)
