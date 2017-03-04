import os
import logging
import pytz
import pytz.exceptions

from django.contrib.auth.decorators import login_required
from django.shortcuts import *
from django.utils import timezone
from django import forms

from .models import *
from statistics.statistics import *
from statistics.goals import Goals
from training import userprof
from training import heatmap


def _make_form(form_type, request, initial=None):
    if request.method == "POST":
        return form_type(request.POST, request.FILES)
    else:
        return form_type(initial=initial)


def index(request):
    if request.user.is_authenticated():
        return redirect('dashboard')
    else:
        return render(request, 'training/index.html', {'users_count': User.objects.all().count()})


@login_required
def user_profile(request):
    current_tz = userprof.timezone(request.user)

    form = _make_form(userprof.UserProfileForm, request, {'timezone': current_tz.zone})

    if request.method == "POST":
        userprof.save_timezone(request.user, request.POST['timezone'])
        return redirect('user_profile')

    return render(request, 'training/user_profile.html', {'form': form})


@login_required
def dashboard(request):
    statistics = Statistics(request.user) # type: Statistics
    goals = Goals(request.user)
    return render(request, 'training/dashboard.html', {'statistics': statistics,
                                                       'goals': goals})


@login_required
def workout(request, training_session_id):
    workout = get_object_or_404(Workout, pk=training_session_id, user=request.user)

    gpx = None
    try:
        gpx = workout.gpx_set.get()
    except:
        pass

    return render(request, 'training/workout.html', {'workout': workout,
                                                     'statistics': Statistics(request.user),
                                                     'gpx': gpx})


@login_required
def delete_workout(request, workout_id):
    workout = Workout.objects.get(pk=workout_id, user=request.user)
    workout.delete()
    return redirect('dashboard')


@login_required
def explorer(request):
    h = heatmap.generate_heatmap(request.user)
    return render(request, 'training/explorer.html', {'heatmap': h})
