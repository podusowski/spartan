import datetime

from django.shortcuts import *
from django.http import HttpResponse

from .models import *

def index(request):
    return render(request, 'training/index.html')

def dashboard(request):
    previous_workouts = Workout.objects.order_by('-pk')
    return render(request, 'training/dashboard.html', {'previous_workouts': previous_workouts,
                                                       'total_workouts': len(Workout.objects.all())})

def start_workout(request):
    s = Workout()
    s.save()
    return redirect('training_session', s.id)

def finish_workout(request, training_session_id):
    s = Workout.objects.get(pk=training_session_id)
    s.finish()
    s.save()
    return redirect('training_session', s.id)

def training_session(request, training_session_id):
    workout = Workout.objects.get(pk=training_session_id)
    return render(request, 'training/workout.html', {'workout': workout, 'most_common_reps': Reps.most_common()[0:4]})

def add_excercise(request, training_session_id):
    s = Workout.objects.get(pk=training_session_id)
    s.excercise_set.create(name=request.POST['name'])
    try:
        s.start()
    except: pass
    s.save()
    return redirect('training_session', training_session_id)

def save_excercise(request, excercise_id):
    s = Excercise.objects.get(pk=excercise_id)
    s.sets = request.POST['sets']
    s.save()
    return redirect('training_session', s.workout.id)

def add_reps(request, excercise_id):
    s = Excercise.objects.get(pk=excercise_id)
    s.reps_set.create(reps=request.POST['reps'])
    return redirect('training_session', s.workout.id)
