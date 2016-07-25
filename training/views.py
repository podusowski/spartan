import datetime

from django.contrib.auth.decorators import login_required
from django.shortcuts import *
from django.http import HttpResponse

from .models import *
from .statistics import *


def index(request):
    if request.user.is_authenticated():
        return redirect('dashboard')
    else:
        return render(request, 'training/index.html', {'users_count': User.objects.all().count()})


@login_required
def dashboard(request):
    return render(request, 'training/dashboard.html', {'previous_workouts': previous_workouts(request),
                                                       'most_common_excercises': most_common_excercises(request),
                                                       'total_reps': total_reps(request),
                                                       'reps_per_week': reps_per_week(request, 5)})


@login_required
def statistics(request):
    return render(request, 'training/statistics.html', {'previous_workouts': previous_workouts(request),
                                                        'most_common_excercises': most_common_excercises(request),
                                                        'reps_per_week': reps_per_week(request, 5)})


@login_required
def start_workout(request):
    workout = Workout.objects.create(user=request.user)
    return redirect('workout', workout.id)


@login_required
def finish_workout(request, training_session_id):
    workout = Workout.objects.get(pk=training_session_id)
    workout.finish()
    workout.save()

    try:
        current_excercise = workout.excercise_set.order_by('-pk')[0]
        current_excercise.time_finished = datetime.datetime.now()
        current_excercise.save()
    except:
        pass

    return redirect('workout', workout.id)


@login_required
def workout(request, training_session_id):
    workout = Workout.objects.get(pk=training_session_id, user=request.user)
    return render(request, 'training/workout.html', {'workout': workout,
                                                     'most_common_reps': Reps.most_common(),
                                                     'most_common_excercises': Excercise.most_common()})


@login_required
def add_excercise(request, training_session_id):
    workout = Workout.objects.get(pk=training_session_id, user=request.user)

    try:
        current_excercise = workout.excercise_set.order_by('-pk')[0]
        current_excercise.time_finished = datetime.datetime.now()
        current_excercise.save()
    except:
        pass

    excercise = workout.excercise_set.create(name=request.POST['name'])
    try:
        workout.start()
    except:
        pass
    workout.save()

    excercise.time_started = datetime.datetime.now()
    excercise.save()

    return redirect('workout', training_session_id)


@login_required
def add_reps(request, excercise_id):
    s = Excercise.objects.get(pk=excercise_id, workout__user=request.user)
    s.reps_set.create(reps=request.POST['reps'])

    s.time_updated = datetime.datetime.now()
    s.save()
    return redirect('workout', s.workout.id)


@login_required
def delete_workout(request, workout_id):
    workout = Workout.objects.get(pk=workout_id, user=request.user)
    workout.delete()
    return redirect('dashboard')
