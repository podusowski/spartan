from django.shortcuts import *
from django.db.models import Sum, Avg

from training import units
from training import models


def redirect_to_workout(workout):
    return redirect('show_strength_workout', workout.id)


def volume(workout):
    reps = models.Reps.objects.filter(excercise__workout=workout).aggregate(Sum('reps'))['reps__sum'] or 0
    return units.Volume(reps=reps)
