from django.db import models


class TrainingSession(models.Model):
    pass


class Excercise(models.Model):
    training_session = models.ForeignKey(TrainingSession)
    name = models.CharField(max_length=200)
    sets = models.CharField(max_length=200)
