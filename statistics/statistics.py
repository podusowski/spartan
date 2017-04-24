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


PopularWorkout = collections.namedtuple('PopularWorkout', ['name', 'count', 'volume', 'earliest', 'latest'])


def _sum_volume(source, volume_field):
    value = source.aggregate(value=Sum(volume_field))['value']
    return value if value else 0


class WorkoutStatistics:
    def __init__(self, user, name):
        self.user = user
        self.name = name
        self._source = Excercise.objects.filter(workout__user=user, name=name)
        self._aggregations = self._basic_aggregations()

    def metrics(self):
        from django.apps import apps
        import importlib

        def get_statistics_from_app(name):
            try:
                app_statistics = importlib.import_module('{}.local_statistics'.format(name))
                logging.debug('looking for stats in {}'.format(name))
                return app_statistics.workout(self.user, self.name)
            except ImportError as e:
                logging.debug('can\'t import app {}'.format(name))

        result = []

        for app in apps.get_app_configs():
            stats = get_statistics_from_app(app.name)
            if stats:
                result.extend(stats)

        return result

    def _basic_aggregations(self):
        return self._source.aggregate(count=Count('name'),
                                      earliest=Min('workout__started'),
                                      latest=Max('workout__started'))

    def _aggregate(self, **kwargs):
        '''
        django can't do multiple aggregation in one expression
        '''
        return self._source.aggregate(**kwargs)

    @property
    def volume(self):
        volume = _sum_volume(self._source, 'reps__reps')
        return units.Volume(reps=volume)

    @property
    def count(self):
        return self._aggregations['count']

    @property
    def earliest(self):
        return self._aggregations['earliest']

    @property
    def average_reps(self):
        return self._aggregate(value=Avg('reps__reps'))['value']


class Statistics:
    def __init__(self, user):
        self.user = user

    def workout_statistics(self, name):
        return WorkoutStatistics(self.user, name)

    def favourites_this_month(self, now=timezone.now()):
        return self.most_popular_workouts(dates.this_month(now))

    def _activities_in_range(self, source, time_range=None):
        source = source.filter(workout__user=self.user)

        if time_range is not None and time_range.fully_bound():
            source = source.filter(workout__started__gte=time_range.start, workout__started__lt=time_range.end)

        return source

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
            volume = _sum_volume(workouts.filter(name=workout['name']), 'distance')

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
            volume = _sum_volume(workouts.filter(name=workout['name']), 'reps__reps')

            return PopularWorkout(name=workout['name'],
                                  count=workout['count'],
                                  volume=units.Volume(reps=volume),
                                  earliest=workout['earliest'],
                                  latest=workout['latest'])

        return [decorate_strength_workout(w) for w in annotated]

    def most_popular_workouts(self, time_range=None) -> Iterable[PopularWorkout]:
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

    def most_common_reps(self, limit=4):
        return sorted(Reps.objects \
                          .values_list('reps') \
                          .annotate(rep_count=Count('reps')) \
                          .order_by('-rep_count', '-reps') \
                          .values_list('reps', flat=True)[:limit], reverse=True)
