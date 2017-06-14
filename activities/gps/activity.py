from django.shortcuts import *

from training import models
from training import units
from . import views


TYPE = 'gps'


def redirect_to_workout(workout):
    return redirect(views.workout, workout.id)


def volume(workout):
    distance = workout.gpx_set.get().distance
    return units.Volume(meters=distance)
