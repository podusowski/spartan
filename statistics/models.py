from django.db import models
from django.contrib.auth.models import User


class Goal(models.Model):
    user = models.ForeignKey(User)
    name = models.CharField(max_length=200)
    volume = models.IntegerField()

    def __str__(self):
        return "{} of {} by {}".format(self.volume, self.name, self.user)
