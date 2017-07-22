from django.shortcuts import *

from training import models
from training import units


TYPE = 'gps'


def redirect_to_workout(workout):
    return redirect('show_gps_workout', workout.id)


def volume(workout):
    distance = workout.gpx_set.get().distance
    return units.Volume(meters=distance)


def color(workout):
    return 'green'
