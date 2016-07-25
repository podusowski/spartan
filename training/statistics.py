import datetime

from django.db.models import Sum

from .models import *


def previous_workouts(request):
    return Workout.objects.filter(user=request.user).order_by('-pk')


def most_common_excercises(request):
    return Excercise.objects.filter(workout__user=request.user).values_list('name').annotate(count=Count('name')).order_by('-count')


def _week_range(number):
    today = datetime.date.today()

    week_start = today - datetime.timedelta(days=today.weekday())
    week = datetime.timedelta(weeks=1)

    while number > 0:
        yield (week_start, week_start + week)
        number -= 1
        week_start -= week


def reps_per_week(request, weeks_number):
    def reps_in_range(time_range):
        begin, end = time_range
        reps = Reps.objects.filter(excercise__workout__user=request.user,
                                   excercise__time_started__gt=begin,
                                   excercise__time_started__lt=end).aggregate(Sum('reps'))['reps__sum']

        return {'time': '{:%d.%m}'.format(end),
                'value': 0 if reps is None else reps}

    return list(map(reps_in_range, _week_range(weeks_number)))

def total_reps(request):
    return Reps.objects.filter(excercise__workout__user=request.user).aggregate(Sum('reps'))['reps__sum']
