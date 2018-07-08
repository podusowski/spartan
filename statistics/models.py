from django.db import models
from django.contrib.auth.models import User


class Goal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    volume = models.IntegerField()

    def __str__(self):
        return "{}'s goal of making {} of {}".format(self.user, self.volume, self.name)
