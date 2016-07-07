from django.db import models

class Excercise(models.Model):
    name = models.CharField(max_length=200)
    sets = models.CharField(max_length=200)
