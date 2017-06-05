from django.shortcuts import *


def redirect_to_workout(workout):
    return redirect('show_strength_workout', workout.id)
