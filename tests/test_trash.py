import os
import datetime
import pytz
import unittest.mock
from unittest.mock import patch, Mock, PropertyMock
import logging

from training import models, units, dates

from tests.utils import time, ClientTestCase
from tests import utils


class TrashTestCase(ClientTestCase):
    def _get_statistics_from_dashboard(self):
        return self.get('/dashboard').context['statistics']

    _start_workout = utils.start_workout
    _strength_workout = utils.strength_workout

    def _import_gpx(self, filename):
        path = os.path.join(utils.GPX_DIR, filename)
        with open(path, 'r') as f:
            return self.post('/gps/upload_gpx/', {'gpxfile': f}).context['workout']

    def test_gpx_import(self):
        workout = self._import_gpx('3p_simplest.gpx')

        self.assertEqual(time(2016, 7, 30, 6, 22, 5), workout.started)
        self.assertEqual(time(2016, 7, 30, 6, 22, 7), workout.finished)

        gpx = workout.gpx_set.get()
        self.assertEqual("running", gpx.name)
        self.assertEqual(4, gpx.distance)
        self.assertEqual(units.Volume(meters=4), workout.volume)
        self.assertEqual('green', workout.color)

    def _import_gpx_and_check_activity_type(self, filename, name):
        workout = self._import_gpx(filename)
        self.assertEqual(name, workout.workout_type)

    def test_import_activity_type_from_gpx(self):
        self._import_gpx_and_check_activity_type('3p_cycling.gpx', 'cycling')
        self._import_gpx_and_check_activity_type('3p_simplest.gpx', 'running')

    def test_most_popular_excercises(self):
        self._import_gpx('3p_simplest.gpx')
        self._import_gpx('3p_simplest_2.gpx')
        self._import_gpx('running_no_points.gpx')

        self._import_gpx('3p_cycling.gpx')

        pushups = self._strength_workout('push-up', [2, 4, 8])
        more_pushups = self._strength_workout('push-up', [1])

        statistics = self._get_statistics_from_dashboard()
        excercises = statistics.most_popular_workouts()

        self.assertEqual('running', excercises[0].name)
        self.assertEqual(3, excercises[0].count)
        self.assertEqual(units.Volume(meters=8), excercises[0].volume)
        self.assertEqual(time(2016, 7, 30, 6, 22, 5), excercises[0].earliest)
        self.assertEqual(time(2016, 8, 30, 6, 22, 5), excercises[0].latest)

        self.assertEqual('push-up', excercises[1].name)
        self.assertEqual(2, excercises[1].count)
        self.assertEqual(units.Volume(reps=15), excercises[1].volume)
        self.assertEqual(pushups.started, excercises[1].earliest)
        self.assertEqual(more_pushups.started, excercises[1].latest)

        self.assertEqual('cycling', excercises[2].name)
        self.assertEqual(1, excercises[2].count)
        self.assertEqual(units.Volume(meters=4), excercises[2].volume)
        self.assertEqual(time(2016, 6, 30, 6, 22, 5), excercises[2].earliest)

    def test_most_popular_gps_workouts_during_timespan(self):
        statistics = self._get_statistics_from_dashboard()

        self._import_gpx('3p_simplest.gpx')
        self._import_gpx('3p_simplest_2.gpx')

        popular = statistics.most_popular_workouts()

        self.assertEqual(units.Volume(meters=8), popular[0].volume)

        popular = statistics.most_popular_workouts(dates.TimeRange(time(2016, 7, 1, 0, 0, 0),
                                                                   time(2016, 7, 30, 23, 59, 59)))

        self.assertEqual(units.Volume(meters=4), popular[0].volume)

    def test_most_popular_strength_workouts_during_timespan(self):
        statistics = self._get_statistics_from_dashboard()

        workout = self._strength_workout('push-up', [5, 10, 7])
        workout.started = time(2016, 7, 1, 0, 0, 0)
        workout.finished = time(2016, 7, 1, 0, 0, 1)
        workout.save()

        workout = self._strength_workout('push-up', [5, 10, 7])
        workout.started = time(2016, 8, 1, 0, 0, 0)
        workout.finished = time(2016, 8, 1, 0, 0, 1)
        workout.save()

        popular = statistics.most_popular_workouts()

        self.assertEqual(units.Volume(reps=44), popular[0].volume)

        popular = statistics.most_popular_workouts(dates.TimeRange(time(2016, 7, 1, 0, 0, 0),
                                                                   time(2016, 7, 30, 23, 59, 59)))

        self.assertEqual(1, popular[0].count)
        self.assertEqual(units.Volume(reps=22), popular[0].volume)

    def test_most_popular_workouts_this_month(self):
        statistics = self._get_statistics_from_dashboard()

        workout = self._strength_workout('push-up', [5, 10, 7])
        workout.started = time(2016, 7, 1, 0, 0, 0)
        workout.finished = time(2016, 7, 1, 0, 0, 1)
        workout.save()

        workout = self._strength_workout('push-up', [5, 10, 7])
        workout.started = time(2016, 8, 1, 0, 0, 0)
        workout.finished = time(2016, 8, 1, 0, 0, 1)
        workout.save()

        self._import_gpx('3p_simplest.gpx')  # 07.2016
        self._import_gpx('3p_simplest_2.gpx')  # 08.2016
        self._import_gpx('3p_cycling.gpx')  # 06.2016

        month = statistics.favourites_this_month(now=time(2016, 7, 31))

        self.assertEqual(2, len(month))
        self.assertEqual('running', month[0].name)
        self.assertEqual(1, month[0].count)
        self.assertEqual(units.Volume(meters=4), month[0].volume)

        self.assertEqual('push-up', month[1].name)
        self.assertEqual(1, month[1].count)
        self.assertEqual(units.Volume(reps=22), month[1].volume)

    def _find_statistics_field(self, name, field):
        statistics = self._get_statistics_from_dashboard()
        workout_statistics = statistics.workout_statistics(name)
        metrics = workout_statistics.metrics()

        for n, value in metrics:
            if n == field:
                return value

        logging.warn('no "{}" in {}'.format(field, metrics))

    def test_strength_statistics(self):
        self.switch_user(self.other_user)

        self._strength_workout('push-up', [1])

        self.switch_user(self.user)

        self._strength_workout('push-up', [1, 2, 3])
        self._strength_workout('push-up', [2, 2])
        self._strength_workout('push-up', [10])

        self.assertEqual(3, self._find_statistics_field('push-up', 'total workouts'))
        self.assertEqual(units.Volume(reps=20), self._find_statistics_field('push-up', 'total reps'))
        self.assertEqual(6, self._find_statistics_field('push-up', 'total series'))
        self.assertEqual(3, self._find_statistics_field('push-up', 'average reps per series'))
        self.assertEqual(7, self._find_statistics_field('push-up', 'average reps per workout'))

    def test_gps_statistics(self):
        self._import_gpx('3p_simplest.gpx')

        self.assertEqual(1, self._find_statistics_field('running', 'total workouts'))
