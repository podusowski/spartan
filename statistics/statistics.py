import datetime
import logging
import arrow
import collections
from typing import Iterable

from django.db.models import Sum, Min, Max
from django.utils import timezone
from django.http import Http404

from training.models import *
from training import units
from training import dates
from . import utils
from activities import registry


class Day:
    def __init__(self, start_time):
        self.start_time = start_time
        self.workouts = []

    def __repr__(self):
        return str(self.workouts)


class Week:
    def __init__(self, statistics, start_time, end_time):
        self.time_range = dates.TimeRange(start_time, end_time)
        self.user = statistics.user

    @property
    def workouts(self):
        user_workouts = Workout.objects.filter(user=self.user)
        return utils.between_timerange(user_workouts, self.time_range, time_field='started')

    @property
    def days(self):

        def make_day(number):
            start_time = self.time_range.start + datetime.timedelta(days=number)
            return Day(start_time)

        def in_past(day):
            return day.start_time <= timezone.now()

        days = [make_day(n) for n in range(7) if in_past(make_day(n))]

        for workout in self.workouts.order_by('started'):
            day = workout.started.weekday()
            days[day].workouts.append(workout)

        return reversed(days)


PopularWorkout = collections.namedtuple('PopularWorkout', ['name', 'count', 'volume', 'earliest', 'latest'])


def workout(user, excercise_name, rng=None):
    result = []
    for app_statistics in registry.modules('local_statistics'):
        stats = app_statistics.workout(user, excercise_name, rng)
        if stats:
            result.extend(stats)

    if not result:
        logging.warning("no stats found for '{}'".format(excercise_name))

    return result


def first_time(user, excercise_name):
    for app_statistics in registry.modules('local_statistics'):
        if hasattr(app_statistics, 'first_time'):
            stats = app_statistics.first_time(user, excercise_name)
            if stats:
                return stats


class Statistics:
    def __init__(self, user):
        self.user = user

    def favourites_this_month(self):
        return self.most_popular_workouts(dates.this_month(timezone.now()))

    def _activities_in_range(self, source, time_range=None):
        return utils.between_timerange(source.filter(workout__user=self.user),
                                       time_range,
                                       time_field='workout__started')

    def _basic_annotations(self, source):
        return source.values('name') \
                     .annotate(count=Count('name'),
                               earliest=Min('workout__started'),
                               latest=Max('workout__started')) \
                     .order_by('-count')

    def _most_popular_gps_workouts(self, time_range) -> Iterable[PopularWorkout]:
        workouts = self._activities_in_range(Gpx.objects, time_range)
        annotated = self._basic_annotations(workouts)

        def decorate_gps_workout(workout):
            volume = utils.sum(workouts.filter(name=workout['name']), 'distance')

            return PopularWorkout(name=workout['name'],
                                  count=workout['count'],
                                  volume=units.Volume(meters=volume),
                                  earliest=workout['earliest'],
                                  latest=workout['latest'])

        return [decorate_gps_workout(w) for w in annotated]

    def _most_popular_strength_workouts(self, time_range) -> Iterable[PopularWorkout]:
        workouts = self._activities_in_range(Excercise.objects, time_range)
        annotated = self._basic_annotations(workouts)

        def decorate_strength_workout(workout):
            volume = utils.sum(workouts.filter(name=workout['name']), 'reps__reps')

            return PopularWorkout(name=workout['name'],
                                  count=workout['count'],
                                  volume=units.Volume(reps=volume),
                                  earliest=workout['earliest'],
                                  latest=workout['latest'])

        return [decorate_strength_workout(w) for w in annotated]

    def most_popular_workouts(self, time_range=None) -> Iterable[PopularWorkout]:
        logging.debug("Getting workout overview withing time range: {}".format(time_range))

        excercises = (self._most_popular_gps_workouts(time_range)
                      + self._most_popular_strength_workouts(time_range))

        return sorted(excercises, key=lambda e: e.count, reverse=True)

    def _first_time_working_out(self):
        workouts = Workout.objects.filter(user=self.user, started__isnull=False)

        try:
            return workouts.earliest("started").started
        except Exception as e:
            logging.warn(str(e))
            return None

    def weeks(self, start=datetime.datetime.utcnow()):
        end_time = self._first_time_working_out()

        logging.debug("building weeks up to {}".format(end_time))

        if end_time is None:
            return []

        return [Week(self, *week_bounds) for week_bounds in dates.week_range(start=start, end=end_time)]

    def not_started_workouts(self):
        return Workout.objects.filter(user=self.user, started__isnull=True)

    def most_common_excercises(self):
        return Excercise.objects.filter(workout__user=self.user).values_list('name').annotate(count=Count('name')).order_by('-count')

    def most_common_reps(self, limit=4):
        return sorted(Reps.objects \
                          .values_list('reps') \
                          .annotate(rep_count=Count('reps')) \
                          .order_by('-rep_count', '-reps') \
                          .values_list('reps', flat=True)[:limit], reverse=True)
