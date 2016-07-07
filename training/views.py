from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return render(request, 'training/index.html')

def train(request):
    return render(request, 'training/train.html')
