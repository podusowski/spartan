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
    reps = models.Reps.objects.filter(excercise__workout=workout).aggregate(Sum('reps'))['reps__sum'] or 0

    if duration:
        return units.Volume(seconds=duration.total_seconds())
    else:
        return units.Volume(reps=reps)
