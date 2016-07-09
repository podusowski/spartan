import datetime

from django.shortcuts import *
from django.http import HttpResponse

from .models import TrainingSession, Excercise

def index(request):
    previous_training_sessions = TrainingSession.objects.order_by('-pk')
    return render(request, 'training/index.html', {'previous_training_sessions': previous_training_sessions})

def start_training_session(request):
    s = TrainingSession()
    s.save()
    return redirect('training_session', s.id)

def finish_training_session(request, training_session_id):
    s = TrainingSession.objects.get(pk=training_session_id)
    s.finish()
    s.save()
    return redirect('training_session', s.id)

def training_session(request, training_session_id):
    s = TrainingSession.objects.get(pk=training_session_id)
    return render(request, 'training/training_session.html', {'training_session': s})

def add_excercise(request, training_session_id):
    s = TrainingSession.objects.get(pk=training_session_id)
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
    return redirect('training_session', s.training_session.id)
