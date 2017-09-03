from django.contrib.auth.decorators import login_required
from django.shortcuts import *

from . import statistics as statistics_mod
from .statistics import Statistics
from .goals import Goals


@login_required
def statistics(request):
    return render(request, 'statistics/statistics.html', {'statistics': Statistics(request.user)})


@login_required
def statistics_this_month(request):
    return render(request, 'statistics/statistics_this_month.html', {'statistics': Statistics(request.user)})


@login_required
def workout(request, name):
    workout = statistics_mod.workout(request.user, name)
    goal = Goals(request.user).get(name)
    return render(request, 'statistics/workout.html', {'name': name, 'workout': workout, 'goal': goal})


@login_required
def goals(request):
    return render(request, 'statistics/goals.html', {'goals': Goals(request.user)})


@login_required
def add_goal(request):
    goals = Goals(request.user)

    if request.method == "POST":
        name = request.POST["name"]

        if not name:
            raise AttributeError()

        volume = int(request.POST["volume"])

        if not volume > 0:
            raise AttributeError()

        goals.set(name, volume)
        return redirect('workout_statistics', name)


@login_required
def delete_goal(request):
    goals = Goals(request.user)

    if request.method == "POST":
        goals.delete(request.POST['name'])
        return redirect('workout_statistics', request.POST['name'])
