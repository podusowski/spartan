from django.shortcuts import *
from django.db.models import Sum, Avg

from training import units
from training import models
from . import views


TYPE = 'strength'


def redirect_to_workout(workout):
    return redirect(views.workout, workout.id)


def volume(workout):
    duration = models.Timers.objects.filter(excercise__workout=workout).aggregate(value=Sum('duration'))['value']
    reps = models.Reps.objects.filter(excercise__workout=workout).aggregate(Sum('reps'))['reps__sum']

    values = []

    if duration:
        values.append(units.Volume(seconds=duration.total_seconds()))

    if reps:
        values.append(units.Volume(reps=reps))

    return units.MultiVolume(values)


def color(workout):
    return 'silver'
