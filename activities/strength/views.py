from django.shortcuts import *
from django.contrib.auth.decorators import login_required

from . import strength_workout


@login_required
def start_workout(request):
    id = strength_workout.start_workout(request.user)
    return redirect('workout', id)


@login_required
def add_excercise(request, training_session_id):
    strength_workout.add_excercise(request.user, training_session_id, request.POST['name'])
    return redirect('workout', training_session_id)


@login_required
def add_reps(request, excercise_id):
    id = strength_workout.add_reps(request.user, excercise_id, request.POST['reps'])
    return redirect('workout', id)


@login_required
def finish_workout(request, training_session_id):
    strength_workout.finish_workout(None, training_session_id)
    return redirect('workout', training_session_id)
