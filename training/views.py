from django.shortcuts import render
from django.http import HttpResponse

from .models import TrainingSession

def index(request):
    return render(request, 'training/index.html')

def train(request, training_session_id):
    s = TrainingSession.objects.get(pk=training_session_id)
    return render(request, 'training/train.html')
