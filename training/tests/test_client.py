import os
import datetime
import pytz

from django.test import Client, TestCase
from django.contrib.auth.models import User

from training import models, units


GPX_DIR = os.path.dirname(os.path.abspath(__file__))


class ClienStrengthTestCase(TestCase):
    def setUp(self):
        user = User.objects.create_user(username='grzegorz', email='', password='z')
        self.client = Client()

    def _get(self, uri, status_code=200):
        response = self.client.get(uri, follow=True)
        self.assertEqual(status_code, response.status_code)
        return response

    def _post(self, uri, data={}, status_code=200):
        response = self.client.post(uri, data, follow=True)
        self.assertEqual(status_code, response.status_code)
        return response

    def _expect_workout_page(self, workout_id, status_code=200):
        return self._get('/workout/{}'.format(workout_id), status_code=status_code)

    def _expect_to_be_logged_in(self):
        self._post('/login/', {'username': 'grzegorz', 'password': 'z'})

    def _start_workout(self):
        workout = self._get('/start_workout').context['workout']
        self._expect_workout_page(workout.id)
        return workout

    def _get_statistics_from_dashboard(self):
        return self._get('/dashboard').context['statistics']

    def test_create_workout_and_delete_it(self):
        self._expect_to_be_logged_in()
        workout = self._start_workout()

        self._post('/delete_workout/{}/'.format(workout.id))

        self._expect_workout_page(workout.id, status_code=404)

    def _do_some_pushups(self, series):
        workout = self._start_workout()

        self._post('/add_excercise/{}/'.format(workout.id), {'name': 'push-up'})

        excercise = workout.excercise_set.latest('pk')

        for reps in series:
            self._post('/add_reps/{}/'.format(excercise.id), {'reps': reps})

        self._post('/finish_workout/{}'.format(workout.id))

    def test_add_some_excercises_and_reps(self):
        self._expect_to_be_logged_in()
        self._start_workout()

        statistics = self._get_statistics_from_dashboard()
        workout = statistics.previous_workouts()[0]

        self.assertIsNone(workout.started)
        self.assertIsNone(workout.finished)

        self._post('/add_excercise/{}/'.format(workout.id), {'name': 'push-up'})

        statistics = self._get_statistics_from_dashboard()
        workout = statistics.previous_workouts()[0]

        self.assertIsNotNone(workout.started)
        self.assertIsNone(workout.finished)

        excercise = workout.excercise_set.latest('pk')

        self._post('/add_reps/{}/'.format(excercise.id), {'reps': '10'})
        self._post('/add_excercise/{}/'.format(workout.id), {'name': 'pull-up'})

        excercise = workout.excercise_set.latest('pk')

        self._post('/add_reps/{}/'.format(excercise.id), {'reps': '5'})
        self._post('/add_reps/{}/'.format(excercise.id), {'reps': '5'})

        self.assertEqual(units.Volume(reps=20), workout.volume())
        self.assertEqual(20, statistics.total_reps())

        self._post('/finish_workout/{}'.format(workout.id))

        statistics = self._get_statistics_from_dashboard()
        workout = statistics.previous_workouts()[0]

        self.assertIsNotNone(workout.started)
        self.assertIsNotNone(workout.finished)

    def _import_gpx(self, filename):
        path = os.path.join(GPX_DIR, filename)
        with open(path, 'r') as f:
            self._post('/upload_gpx/', {'gpxfile': f})

    def _get_latest_workout_from_dashboard(self):
        statistics = self._get_statistics_from_dashboard()
        self.assertTrue(statistics.previous_workouts().count() > 0)
        return statistics.previous_workouts()[0]

    def test_gpx_import(self):
        self._expect_to_be_logged_in()

        self._import_gpx('3p_simplest.gpx')

        workout = self._get_latest_workout_from_dashboard()

        self.assertTrue(workout.is_gpx());
        self.assertEqual(datetime.datetime(2016, 7, 30, 6, 22, 5, tzinfo=pytz.utc), workout.started)
        self.assertEqual(datetime.datetime(2016, 7, 30, 6, 22, 7, tzinfo=pytz.utc), workout.finished)

        gpx_workout = workout.gpx_set.get()
        self.assertEqual("running", gpx_workout.activity_type.lower())
        self.assertEqual(4, gpx_workout.distance)

        statistics = self._get_statistics_from_dashboard()
        self.assertEqual('4m', statistics.total_km())

        self._import_gpx('3p_simplest_2.gpx')
        self.assertEqual('8m', statistics.total_km())

        self._import_gpx('3p_cycling.gpx')
        self.assertEqual('12m', statistics.total_km())

    def _import_gpx_and_check_activity_type(self, filename, activity_type):
        self._import_gpx(filename)
        workout = self._get_latest_workout_from_dashboard()
        self.assertEqual(activity_type, workout.workout_type)

    def test_import_activity_type_from_gpx(self):
        self._expect_to_be_logged_in()

        self._import_gpx_and_check_activity_type('3p_cycling.gpx', 'cycling')
        self._import_gpx_and_check_activity_type('3p_simplest.gpx', 'running')

    def test_strength_workout_type_when_starting_workout(self):
        self._expect_to_be_logged_in()
        self._start_workout()

        workout = self._get_latest_workout_from_dashboard()
        self.assertEqual('strength', workout.workout_type)

    def test_most_popular_excercises(self):
        self._expect_to_be_logged_in()

        self._import_gpx('3p_simplest.gpx')
        self._import_gpx('3p_simplest_2.gpx')
        self._import_gpx('3p_without_points.gpx')

        self._import_gpx('3p_cycling.gpx')

        self._do_some_pushups([2, 4, 8])

        statistics = self._get_statistics_from_dashboard()
        excercises = statistics.most_popular_workouts()

        self.assertEqual(('running', 3, units.Volume(meters=8)), excercises[0])
        self.assertEqual(('cycling', 1, units.Volume(meters=4)), excercises[1])
        self.assertEqual(('push-up', 1, units.Volume(reps=14)), excercises[2])
