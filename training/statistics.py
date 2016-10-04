import datetime
import logging
import arrow

from django.db.models import Sum
from django.utils import timezone

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


def week_range(number:int=None, end=None, start=timezone.now()):
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


class Day:
    def __init__(self, start_time):
        self.start_time = start_time
        self.workouts = []

    def __repr__(self):
        return str(self.workouts)


class Week:
    def __init__(self, statistics, start_time, end_time):
        self.statistics = statistics
        self.start_time = start_time
        self.end_time = end_time

    @property
    def workouts(self):
        return self.statistics.previous_workouts(self.start_time, self.end_time)

    @property
    def days(self):

        def make_day(number):
            start_time = self.start_time + datetime.timedelta(days=number)
            return Day(start_time)

        result = list(map(make_day, range(7)))

        for workout in self.workouts:
            day = workout.started.weekday()
            result[day].workouts.append(workout)

        logging.debug(str(result))

        return reversed(result)


class Statistics:
    def __init__(self, user):
        self.user = user

    def total_reps(self):
        return Reps.objects.filter(excercise__workout__user=self.user).aggregate(Sum('reps'))['reps__sum']

    def total_km(self):
        meters = Gpx.objects.filter(workout__user=self.user).aggregate(Sum('distance'))['distance__sum']
        return units.km_from_m(meters)

    def _total_distance(self, workout_type):
        meters = Gpx.objects.filter(workout__user=self.user,
                                    activity_type=workout_type).aggregate(value=Sum('distance'))['value']

        return units.Volume(meters=meters)

    def _total_reps(self, excercise_name):
        reps = Reps.objects.filter(excercise__workout__user=self.user,
                                   excercise__name=excercise_name).aggregate(value=Sum('reps'))['value']

        return units.Volume(reps=reps if reps else 0)

    def most_popular_workouts(self):
        gps_workouts = Gpx.objects \
                          .filter(workout__user=self.user) \
                          .values_list('activity_type') \
                          .annotate(count=Count('activity_type')) \
                          .order_by('-count')

        strength_workouts = Excercise.objects \
                                     .filter(workout__user=self.user) \
                                     .values_list('name') \
                                     .annotate(count=Count('name')) \
                                     .order_by('-count')

        def decorate_with_volume(workout):
            workout_type, count = workout
            return workout_type.lower(), count, self._total_distance(workout_type)

        def decorate_strength_workout(workout):
            excercise_name, count = workout
            return excercise_name.lower(), count, self._total_reps(excercise_name)

        return list(map(decorate_with_volume, gps_workouts)) + list(map(decorate_strength_workout, strength_workouts))

    def weeks(self, start=datetime.datetime.utcnow()):

        def make_week(week_bounds):
            return Week(self, *week_bounds)

        _, end_time = workouts_time_bounds(self.user)

        logging.debug("building weeks up to {}".format(end_time))

        if end_time is None:
            return []

        result = list(map(make_week, week_range(start=start, end=end_time)))

        return result

    def reps_per_week(self):
        def reps_in_range(time_range):
            begin, end = time_range
            reps = Reps.objects.filter(excercise__workout__user=self.user,
                                       excercise__time_started__gt=begin,
                                       excercise__time_started__lt=end).aggregate(Sum('reps'))['reps__sum']

            return {'time': '{:%d.%m}'.format(end),
                    'value': 0 if reps is None else reps}

        return list(map(reps_in_range, week_range(5)))

    def previous_workouts(self, begin=None, end=None):
        if begin is not None and end is not None:
            return Workout.objects.filter(user=self.user,
                                          started__gt=begin,
                                          started__lt=end).order_by('-started')
        else:
            return Workout.objects.filter(user=self.user).order_by('-started')

    def not_started_workouts(self):
        return Workout.objects.filter(user=self.user, started__isnull=True)

    def most_common_excercises(self):
        return Excercise.objects.filter(workout__user=self.user).values_list('name').annotate(count=Count('name')).order_by('-count')
