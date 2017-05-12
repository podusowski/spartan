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
    def _view_workout(self, workout_id, status_code=200):
        return self.get('/workout/{}'.format(workout_id), status_code=status_code)

    def _start_workout(self):
        workout = self.get('/strength/start_workout').context['workout']
        self._view_workout(workout.id)
        return workout

    def _get_statistics_from_dashboard(self):
        return self.get('/dashboard').context['statistics']

    def _strength_workout(self, name, series):
        workout = self._start_workout()

        self.post('/strength/add_excercise/{}/'.format(workout.id), {'name': name})

        excercise = workout.excercise_set.latest('pk')

        for reps in series:
            self.post('/strength/add_reps/{}/'.format(excercise.id), {'reps': reps})

        return self.post('/strength/finish_workout/{}'.format(workout.id)).context['workout']

    def _do_some_pushups(self, series):
        return self._strength_workout('push-up', series)

    def test_finish_workout_without_any_excercise(self):
        workout = self._start_workout()

        with self.assertRaises(Exception):
            self.post('/strength/finish_workout/{}'.format(workout.id))

    def _import_gpx(self, filename):
        path = os.path.join(utils.GPX_DIR, filename)
        with open(path, 'r') as f:
            self.post('/gps/upload_gpx/', {'gpxfile': f})

    def _get_latest_workout_from_dashboard(self):
        statistics = self._get_statistics_from_dashboard()
        self.assertTrue(statistics.previous_workouts().count() > 0)
        return statistics.previous_workouts()[0]

    def test_gpx_import(self):
        self._import_gpx('3p_simplest.gpx')

        workout = self._get_latest_workout_from_dashboard()

        self.assertTrue(workout.is_gpx());
        self.assertEqual(time(2016, 7, 30, 6, 22, 5), workout.started)
        self.assertEqual(time(2016, 7, 30, 6, 22, 7), workout.finished)

        gpx_workout = workout.gpx_set.get()
        self.assertEqual("running", gpx_workout.name)
        self.assertEqual(4, gpx_workout.distance)

    def _import_gpx_and_check_activity_type(self, filename, name):
        self._import_gpx(filename)
        workout = self._get_latest_workout_from_dashboard()
        self.assertEqual(name, workout.workout_type)

    def test_import_activity_type_from_gpx(self):
        self._import_gpx_and_check_activity_type('3p_cycling.gpx', 'cycling')
        self._import_gpx_and_check_activity_type('3p_simplest.gpx', 'running')

    def test_strength_workout_type_when_starting_workout(self):
        self._start_workout()

        workout = self._get_latest_workout_from_dashboard()
        self.assertEqual('strength', workout.workout_type)

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

    def test_most_common_reps(self):
        statistics = self._get_statistics_from_dashboard()

        self.assertEqual([], list(statistics.most_common_reps()))

        self._do_some_pushups([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        self.assertEqual([10, 9, 8], list(statistics.most_common_reps(3)))

        self._do_some_pushups([11])
        self.assertEqual([11, 10, 9], list(statistics.most_common_reps(3)))

        self._do_some_pushups([10, 10, 10])
        self.assertEqual([11, 10, 9], list(statistics.most_common_reps(3)))

        self._do_some_pushups([1, 1, 1])
        self.assertEqual([11, 10, 1], list(statistics.most_common_reps(3)))

    def test_showing_empty_explorer_page(self):
        self.get('/explorer')

    def test_connect_to_endomondo(self):
        with patch('endoapi.endomondo.Endomondo') as endomondo:
            endomondo_mock = Mock()
            endomondo.return_value = endomondo_mock
            endomondo.return_value.token = 'token'

            key = self.get('/gps/endomondo/').context['key']
            self.assertIsNone(key)

            self.post('/gps/endomondo/', {'email': 'legan@com.pl', 'password': 'haslo'})
            endomondo.assert_called_with(email='legan@com.pl', password='haslo')

            key = self.get('/gps/endomondo/').context['key']
            self.assertEqual('token', key.key)

            key = self.get('/gps/disconnect_endomondo/').context['key']
            self.assertIsNone(key)

    def test_import_from_endomondo_no_workouts(self):
        with patch('endoapi.endomondo.Endomondo', autospec=True) as endomondo:
            endomondo.return_value = Mock()
            endomondo.return_value.token = 'token'

            self.post('/gps/endomondo/', {'email': 'legan@com.pl', 'password': 'haslo'})

            endomondo.return_value.fetch.return_value = []
            self.get('/gps/synchronize_endomondo_ajax/')

            endomondo.return_value.fetch.assert_called_once_with(max_results=10, before=None, after=None)

            statistics = self._get_statistics_from_dashboard()
            self.assertEqual(0, len(statistics.previous_workouts()))

    def test_import_many_workouts_from_endomondo(self):

        def make_endomondo_workout(i):

            class EndomondoWorkout:
                pass

            workout = EndomondoWorkout()
            workout.id = i
            workout.sport = "running"
            workout.distance = 10
            workout.start_time = time(2016, 1, 1, 0, 0, 0)
            workout.duration = datetime.timedelta(seconds=i)
            workout.points = []

            return workout

        with patch('endoapi.endomondo.Endomondo', autospec=True) as endomondo:
            endomondo.return_value = Mock()
            endomondo.return_value.token = 'token'

            self.post('/gps/endomondo/', {'email': 'legan@com.pl', 'password': 'haslo'})

            endomondo.return_value.fetch.return_value = [make_endomondo_workout(i) for i in range(10)]
            self.get('/gps/synchronize_endomondo_ajax/')

            endomondo.return_value.fetch.assert_called_once_with(max_results=10, before=None, after=None)

            statistics = self._get_statistics_from_dashboard()
            self.assertEqual(10, len(statistics.previous_workouts()))

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


class StrengthWorkoutTestCase(ClientTestCase):
    def _start_workout(self):
        workout = self.get('/strength/start_workout').context['workout']
        self._view_workout(workout.id)
        return workout

    def _view_workout(self, workout_id, status_code=200):
        return self.get('/workout/{}'.format(workout_id), status_code=status_code)

    def test_create_workout_and_delete_it(self):
        workout = self._start_workout()
        self.post('/delete_workout/{}/'.format(workout.id))

        self._view_workout(workout.id, status_code=404)

    def _get_statistics_from_dashboard(self):
        return self.get('/dashboard').context['statistics']

    def test_add_some_excercises_and_reps(self):
        self._start_workout()

        statistics = self._get_statistics_from_dashboard()
        workout = statistics.previous_workouts()[0]

        self.assertIsNone(workout.started)
        self.assertIsNone(workout.finished)

        self.post('/strength/add_excercise/{}/'.format(workout.id), {'name': 'push-up'})

        statistics = self._get_statistics_from_dashboard()
        workout = statistics.previous_workouts()[0]

        self.assertIsNotNone(workout.started)
        self.assertIsNone(workout.finished)

        excercise = workout.excercise_set.latest('pk')

        self.post('/strength/add_reps/{}/'.format(excercise.id), {'reps': '10'})
        self.post('/strength/add_excercise/{}/'.format(workout.id), {'name': 'pull-up'})

        excercise = workout.excercise_set.latest('pk')

        self.post('/strength/add_reps/{}/'.format(excercise.id), {'reps': '5'})
        self.post('/strength/add_reps/{}/'.format(excercise.id), {'reps': '5'})

        self.assertEqual(units.Volume(reps=20), workout.volume())

        self.post('/strength/finish_workout/{}'.format(workout.id))

        statistics = self._get_statistics_from_dashboard()
        workout = statistics.previous_workouts()[0]

        self.assertIsNotNone(workout.started)
        self.assertIsNotNone(workout.finished)

    def test_undo_last_rep(self):
        workout = self._start_workout()

        self.post('/strength/add_excercise/{}/'.format(workout.id), {'name': 'push-up'})
        excercise = workout.excercise_set.latest('pk')

        self.post('/strength/add_reps/{}/'.format(excercise.id), {'reps': '2'})
        self.post('/strength/add_reps/{}/'.format(excercise.id), {'reps': '3'})
        self.assertEqual(units.Volume(reps=5), workout.volume())

        self.post('/strength/undo/{}'.format(workout.id))
        self.assertEqual(units.Volume(reps=2), workout.volume())

    def test_undo_last_excercise(self):
        workout = self._start_workout()

        self.post('/strength/add_excercise/{}/'.format(workout.id), {'name': 'push-up'})
        self.assertEqual(1, workout.excercise_set.count())

        self.post('/strength/undo/{}'.format(workout.id))
        self.assertEqual(0, workout.excercise_set.count())

    def test_undo_does_nothing_where_there_is_nothing_to_do(self):
        workout = self._start_workout()
        self.post('/strength/undo/{}'.format(workout.id))
        self.assertEqual(0, workout.excercise_set.count())


class UserProfileTestCase(ClientTestCase):
    def test_user_profile(self):
        with self.assertRaises(Exception):
            self.user.userprofile

        # page is accessible without post data
        self.get('/user_profile')

    def test_saving_timezone(self):
        self.post('/user_profile', {'timezone': 'Europe/Warsaw'})
        profile = models.UserProfile.objects.get(user=self.user)
        self.assertEqual('Europe/Warsaw', profile.timezone)

        self.post('/user_profile', {'timezone': 'Europe/Lisbon'})
        profile = models.UserProfile.objects.get(user=self.user)
        self.assertEqual('Europe/Lisbon', profile.timezone)

        form = self.get('/user_profile').context['form']
        self.assertEqual('Europe/Lisbon', form.initial['timezone'])

    def test_saving_invalid_timezone_falls_back_to_utc(self):
        self.post('/user_profile', {'timezone': 'invalid'})
        profile = models.UserProfile.objects.get(user=self.user)
        self.assertEqual('UTC', profile.timezone)

        form = self.get('/user_profile').context['form']
        self.assertEqual('UTC', form.initial['timezone'])
