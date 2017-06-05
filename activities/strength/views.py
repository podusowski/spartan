from django.shortcuts import *
from django.contrib.auth.decorators import login_required

from . import strength_workout
import training.models
from statistics.statistics import *


@login_required
def workout(request, workout_id):
    workout = get_object_or_404(training.models.Workout, pk=workout_id, user=request.user)

    return render(request, 'training/workout.html', {'workout': workout,
                                                     'statistics': Statistics(request.user)})


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
def start_timer(request, excercise_id):
    workout_id = strength_workout.start_timer(request.user, excercise_id)
    return redirect('workout', workout_id)


@login_required
def stop_timer(request, excercise_id):
    workout_id = strength_workout.stop_timer(request.user, excercise_id)
    return redirect('workout', workout_id)


@login_required
def undo(request, workout_id):
    strength_workout.undo(request.user, workout_id)
    return redirect('workout', workout_id)


@login_required
def finish_workout(request, training_session_id):
    strength_workout.finish_workout(None, training_session_id)
    return redirect('workout', training_session_id)
