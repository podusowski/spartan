import datetime

from django.contrib.auth.decorators import login_required
from django.shortcuts import *
from django.http import HttpResponse

from .models import *


def index(request):
    if request.user.is_authenticated():
        return redirect('dashboard')
    else:
        return render(request, 'training/index.html')


@login_required
def dashboard(request):
    previous_workouts = Workout.objects.order_by('-pk')
    return render(request, 'training/dashboard.html', {'previous_workouts': previous_workouts,
                                                       'total_workouts': len(Workout.objects.all())})


@login_required
def start_workout(request):
    s = Workout()
    s.user = request.user
    s.save()
    return redirect('training_session', s.id)


@login_required
def finish_workout(request, training_session_id):
    s = Workout.objects.get(pk=training_session_id)
    s.finish()
    s.save()
    return redirect('training_session', s.id)


@login_required
def training_session(request, training_session_id):
    workout = Workout.objects.get(pk=training_session_id, user=request.user)
    return render(request, 'training/workout.html', {'workout': workout, 'most_common_reps': Reps.most_common()})


@login_required
def add_excercise(request, training_session_id):
    s = Workout.objects.get(pk=training_session_id, user=request.user)
    s.excercise_set.create(name=request.POST['name'])
    try:
        s.start()
    except:
        pass
    s.save()
    return redirect('training_session', training_session_id)


@login_required
def save_excercise(request, excercise_id):
    s = Excercise.objects.get(pk=excercise_id, user=request.user)
    s.sets = request.POST['sets']
    s.save()
    return redirect('training_session', s.workout.id)


@login_required
def add_reps(request, excercise_id):
    s = Excercise.objects.get(pk=excercise_id, user=request.user)
    s.reps_set.create(reps=request.POST['reps'])
    return redirect('training_session', s.workout.id)
