from django.shortcuts import *
from django.http import HttpResponse

from .models import TrainingSession, Excercise

def index(request):
    previous_training_sessions = TrainingSession.objects.all()
    return render(request, 'training/index.html', {'previous_training_sessions': previous_training_sessions})

def start_training_session(request):
    s = TrainingSession()
    s.save()
    return redirect('train', s.id)

def train(request, training_session_id):
    s = TrainingSession.objects.get(pk=training_session_id)
    return render(request, 'training/train.html', {'training_session': s})

def add_excercise(request, training_session_id):
    s = TrainingSession.objects.get(pk=training_session_id)
    s.excercise_set.create()
    s.save()
    return redirect('train', training_session_id)

def save_excercise(request, excercise_id):
    s = Excercise.objects.get(pk=excercise_id)
    s.sets = request.POST['sets']
    s.save()
    return redirect('train', s.training_session.id)
