from django.db import models
from django.contrib.auth.models import User

from exper.models import Session

class SessionTimer(models.Model):
    timer_type = models.IntegerField(default=0)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(null=True, blank=True)

    RUNNING_START = 1
    def __str__(self):
        return self.name