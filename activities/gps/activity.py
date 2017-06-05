from django.shortcuts import *

from training import models


TYPE = 'gps'


def redirect_to_workout(workout):
    return redirect('show_gps_workout', workout.id)
