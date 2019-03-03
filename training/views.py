import os
import logging
import pytz
import pytz.exceptions
import importlib

from django.contrib.auth.decorators import login_required
from django.shortcuts import *
from django.utils import timezone
from django.apps import apps
from django import forms
from django.core.paginator import Paginator

from .models import *
from statistics.statistics import *
from statistics.goals import Goals
from training import userprof
from training import heatmap
from training import dates
import activities.registry


def _make_form(form_type, request, initial=None):
    if request.method == "POST":
        return form_type(request.POST, request.FILES)
    else:
        return form_type(initial=initial)


def index(request):
    if request.user.is_authenticated:
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

    paginator = Paginator(statistics.weeks(), 4)
    page = request.GET.get("page")
    weeks = paginator.get_page(page)

    return render(request, 'training/dashboard.html', {'statistics': statistics,
                                                       'goals': goals,
                                                       'days_left_in_this_month': dates.days_left_in_this_month(),
                                                       'weeks': weeks})


@login_required
def new_dashboard(request):
    statistics = Statistics(request.user) # type: Statistics
    goals = Goals(request.user)

    paginator = Paginator(Workout.objects.filter(user=request.user), 20)
    page = request.GET.get("page")
    workouts = paginator.get_page(page)

    return render(request, 'training/new_dashboard.html', {'statistics': statistics,
                                                       'goals': goals,
                                                       'days_left_in_this_month': dates.days_left_in_this_month(),
                                                       'workouts': workouts})


@login_required
def new_activity(request):
    return render(request, 'training/new_activity.html')


@login_required
def workout(request, training_session_id):
    workout = get_object_or_404(Workout, pk=training_session_id, user=request.user)
    activity_module = activities.registry.import_module(workout)
    return activity_module.redirect_to_workout(workout)


@login_required
def edit_workout(request, workout_id):
    workout = get_object_or_404(Workout, pk=workout_id, user=request.user)
    workout.description = request.POST["description"]
    workout.save()

    activity_module = activities.registry.import_module(workout)
    return activity_module.redirect_to_workout(workout)


@login_required
def delete_workout(request, workout_id):
    workout = Workout.objects.get(pk=workout_id, user=request.user)
    workout.delete()
    return redirect('dashboard')


@login_required
def explorer(request):
    h = heatmap.generate_heatmap(request.user)
    return render(request, 'training/explorer.html', {'heatmap': h})
