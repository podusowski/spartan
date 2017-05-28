from django.shortcuts import *

from training import models


def supported(workout):
    return workout.gpx_set.count() > 0


def redirect_to_workout(workout):
    return redirect('show_gps_workout', workout.id)
