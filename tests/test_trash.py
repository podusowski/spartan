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
    _import_gpx = utils.import_gpx

    def test_gpx_import(self):
        workout = self._import_gpx('3p_simplest.gpx')

        self.assertEqual(time(2016, 7, 30, 6, 22, 5), workout.started)
        self.assertEqual(time(2016, 7, 30, 6, 22, 7), workout.finished)

        gpx = workout.gpx_set.get()
        self.assertEqual("running", gpx.name)
        self.assertEqual(4, gpx.distance)
        self.assertEqual(units.Volume(meters=4), workout.volume)
        self.assertEqual('green', workout.color)

    def test_color_for_cycling(self):
        workout = self._import_gpx('3p_cycling.gpx')

        gpx = workout.gpx_set.get()
        self.assertEqual("cycling", gpx.name)
        self.assertEqual('red', workout.color)

    def _import_gpx_and_check_activity_type(self, filename, name):
        workout = self._import_gpx(filename)
        self.assertEqual(name, workout.workout_type)

    def test_import_activity_type_from_gpx(self):
        self._import_gpx_and_check_activity_type('3p_cycling.gpx', 'cycling')
        self._import_gpx_and_check_activity_type('3p_simplest.gpx', 'running')

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
