from django.db import models
from django.db.models import Count
from django.contrib.auth.models import User
from django.template import defaultfilters
from django.db.models import Sum

class Gpx(models.Model):
    user = models.ForeignKey(User)
    gpx = models.FileField(upload_to='gpx')
