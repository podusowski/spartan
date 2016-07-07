from django.shortcuts import render
from django.http import HttpResponse

def train(request):
    return HttpResponse("Training")
