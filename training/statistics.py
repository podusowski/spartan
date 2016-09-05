import datetime
import logging
import arrow

from django.db.models import Sum

from .models import *
from . import units


def workouts_time_bounds(user):
    workouts = Workout.objects.filter(user=user, started__isnull=False)

    try:
        latest_workout = workouts.latest("started")
        earliest_workout = workouts.earliest("started")

        return latest_workout.started, earliest_workout.started

    except Exception as e:
        logging.warn(str(e))
        return None, None


def week_range(number=None, end=None, start=datetime.datetime.utcnow()):
    if number is None and end is None:
        raise AttributeError("number or end parameter must be provided")

    week_start = arrow.get(start).floor('week').datetime
    week = datetime.timedelta(weeks=1)
    second = datetime.timedelta(seconds=1)

    while True:
        yield (week_start, week_start + week - second)
        week_start -= week

        if end is not None and week_start < end:
            break

        if number is not None:
            number -= 1
            if number <= 0:
                break


def weeks(user):
    def make_week(week_bounds):
        start_time, end_time = week_bounds
        workouts = previous_workouts(user, start_time, end_time)
        return {'workouts': workouts}

    _, end_time = workouts_time_bounds(user)

    logging.debug("building weeks up to {}".format(end_time))

    if end_time is None:
        return []

    return map(make_week, week_range(end=end_time))


def previous_workouts(user, begin=None, end=None):
    if begin is not None and end is not None:
        return Workout.objects.filter(user=user,
                                      started__gt=begin,
                                      started__lt=end).order_by('-started')
    else:
        return Workout.objects.filter(user=user).order_by('-started')


def most_common_excercises(request):
    return Excercise.objects.filter(workout__user=request.user).values_list('name').annotate(count=Count('name')).order_by('-count')


def reps_per_week(request, weeks_number):
    def reps_in_range(time_range):
        begin, end = time_range
        reps = Reps.objects.filter(excercise__workout__user=request.user,
                                   excercise__time_started__gt=begin,
                                   excercise__time_started__lt=end).aggregate(Sum('reps'))['reps__sum']

        return {'time': '{:%d.%m}'.format(end),
                'value': 0 if reps is None else reps}

    return list(map(reps_in_range, week_range(weeks_number)))


def total_reps(request):
    return Reps.objects.filter(excercise__workout__user=request.user).aggregate(Sum('reps'))['reps__sum']


def total_km(request):
    meters = Gpx.objects.filter(workout__user=request.user).aggregate(Sum('length_2d'))['length_2d__sum']
    return units.km_from_m(meters)
