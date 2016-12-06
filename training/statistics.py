import datetime
import logging
import arrow

from django.db.models import Sum, Min, Max
from django.utils import timezone

from .models import *
from . import units
from . import dates


def workouts_time_bounds(user):
    workouts = Workout.objects.filter(user=user, started__isnull=False)

    try:
        latest_workout = workouts.latest("started")
        earliest_workout = workouts.earliest("started")

        return latest_workout.started, earliest_workout.started

    except Exception as e:
        logging.warn(str(e))
        return None, None


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

        def in_past(day):
            return day.start_time <= timezone.now()

        days = [make_day(n) for n in range(7) if in_past(make_day(n))]

        for workout in self.workouts.order_by('started'):
            day = workout.started.weekday()
            days[day].workouts.append(workout)

        return reversed(days)


def _filter_by_timespan(source, start, end):
    if start is not None and end is not None:
        return source.filter(workout__started__gte=start, workout__started__lt=end)
    else:
        return source


class Statistics:
    def __init__(self, user):
        self.user = user

    def favourites_this_month(self, now=timezone.now()):
        months = list(dates.month_range(1, start=now))
        return self.most_popular_workouts(*months[0])

    def _gps_workouts(self, time_begin=None, time_end=None):
        return _filter_by_timespan(Gpx.objects, time_begin, time_end).filter(workout__user=self.user)

    def _strength_workouts(self, time_begin=None, time_end=None):
        return _filter_by_timespan(Excercise.objects, time_begin, time_end).filter(workout__user=self.user)

    def most_popular_workouts(self, time_begin=None, time_end=None):
        gps_workouts = self._gps_workouts(time_begin, time_end) \
                           .values('activity_type') \
                           .annotate(count=Count('activity_type'),
                                     earliest=Min('workout__started'),
                                     latest=Max('workout__started')) \
                           .order_by('-count')

        strength_workouts = self._strength_workouts(time_begin, time_end) \
                                .values('name') \
                                .annotate(count=Count('name'),
                                          earliest=Min('workout__started'),
                                          latest=Max('workout__started')) \
                                .order_by('-count')

        def total_distance(workout_type):
            meters = self._gps_workouts(time_begin, time_end) \
                         .filter(activity_type=workout_type) \
                         .aggregate(value=Sum('distance'))['value']

            return units.Volume(meters=meters if meters else 0)

        def total_reps(excercise_name):
            reps = self._strength_workouts(time_begin, time_end) \
                       .filter(name=excercise_name) \
                       .aggregate(value=Sum('reps__reps'))['value']

            return units.Volume(reps=reps if reps else 0)

        def decorate_gps_workout(workout):
            return {'name': workout['activity_type'],
                    'count': workout['count'],
                    'volume': total_distance(workout['activity_type']),
                    'earliest': workout['earliest'],
                    'latest': workout['latest']}

        def decorate_strength_workout(workout):
            return {'name': workout['name'],
                    'count': workout['count'],
                    'volume': total_reps(workout['name']),
                    'earliest': workout['earliest'],
                    'latest': workout['latest']}

        excercises = (list(map(decorate_gps_workout, gps_workouts))
                    + list(map(decorate_strength_workout, strength_workouts)))

        return sorted(excercises, key=lambda e: e['count'], reverse=True)

    def weeks(self, start=datetime.datetime.utcnow()):

        def make_week(week_bounds):
            return Week(self, *week_bounds)

        _, end_time = workouts_time_bounds(self.user)

        logging.debug("building weeks up to {}".format(end_time))

        if end_time is None:
            return []

        result = list(map(make_week, dates.week_range(start=start, end=end_time)))

        return result

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

    def most_common_reps(self):
        return sorted(Reps.objects \
                          .values_list('reps') \
                          .annotate(rep_count=Count('reps')) \
                          .order_by('-rep_count', '-reps') \
                          .values_list('reps', flat=True)[:10], reverse=True)
