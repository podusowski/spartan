from django.contrib.auth.decorators import login_required
from django.shortcuts import *

from . import statistics as statistics_mod
from .statistics import Statistics
from .goals import Goals
from training.dates import TimeRange, month_range


@login_required
def statistics(request):
    return render(request, 'statistics/statistics.html', {'statistics': Statistics(request.user)})


@login_required
def statistics_this_month(request):
    return render(request, 'statistics/statistics_this_month.html', {'statistics': Statistics(request.user)})


@login_required
def workout(request, name, rng=None):
    if rng is not None:
        rng = TimeRange.fromurl(rng)

    workout = statistics_mod.workout(request.user, name, rng)
    goal = Goals(request.user).get(name)

    first_time = statistics_mod.first_time(request.user, name)

    timeranges = []
    if first_time is not None:
        timeranges = list(month_range(end=first_time))

    return render(request, 'statistics/workout.html', {'name': name,
                                                       'workout': workout,
                                                       'goal': goal,
                                                       'timeranges': timeranges,
                                                       'rng': rng})


@login_required
def metric_chart(request, excercise_name, metric_name):
    chart = statistics_mod.metric_chart(request.user, excercise_name, metric_name)

    return render(request, 'statistics/metric_chart.html', {'name': excercise_name,
                                                            'metric': metric_name,
                                                            'data': chart})


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
