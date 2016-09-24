from django.test import Client, TestCase
from django.contrib.auth.models import User

from training import models, units


class ClienStrengthTestCase(TestCase):
    def setUp(self):
        user = User.objects.create_user(username='grzegorz', email='', password='z')
        self.client = Client()

    def _expect_workout_page(self, workout_id, status_code=200):
        response = self.client.get('/workout/{}'.format(workout_id), follow=True)
        self.assertEqual(status_code, response.status_code)

    def _expect_to_be_logged_in(self):
        response = self.client.post('/login/', {'username': 'grzegorz', 'password': 'z'})
        self.assertEqual(302, response.status_code)
        self.assertEqual('/dashboard', response['Location'])

    def _expect_workout_to_be_created(self):
        response = self.client.get('/start_workout', follow=True)
        self.assertEqual(200, response.status_code)
        self.assertIsNotNone(response.context['workout'])

        workout_id = response.context['workout'].id

        self._expect_workout_page(workout_id)

    def _expect_statistics_from_dashboard(self):
        response = self.client.post('/dashboard', follow=True)
        self.assertEqual(200, response.status_code)
        return response.context['statistics']

    def test_create_workout_and_delete_it(self):
        self._expect_to_be_logged_in()
        self._expect_workout_to_be_created()

        statistics = self._expect_statistics_from_dashboard()
        workout = statistics.previous_workouts()[0]

        response = self.client.post('/delete_workout/{}/'.format(workout.id), follow=True)
        self.assertEqual(200, response.status_code)

        self._expect_workout_page(workout.id, status_code=404)

    def test_add_some_excercises_and_reps(self):
        self._expect_to_be_logged_in()
        self._expect_workout_to_be_created()

        statistics = self._expect_statistics_from_dashboard()
        workout = statistics.previous_workouts()[0]

        self.assertIsNone(workout.started)
        self.assertIsNone(workout.finished)

        response = self.client.post('/add_excercise/{}/'.format(workout.id), {'name': 'push-up'}, follow=True)
        self.assertEqual(200, response.status_code)

        statistics = self._expect_statistics_from_dashboard()
        workout = statistics.previous_workouts()[0]

        self.assertIsNotNone(workout.started)
        self.assertIsNone(workout.finished)

        excercise = workout.excercise_set.latest('pk')
        response = self.client.post('/add_reps/{}/'.format(excercise.id), {'reps': '10'}, follow=True)
        self.assertEqual(200, response.status_code)

        response = self.client.post('/add_excercise/{}/'.format(workout.id), {'name': 'pull-up'}, follow=True)
        self.assertEqual(200, response.status_code)

        excercise = workout.excercise_set.latest('pk')
        response = self.client.post('/add_reps/{}/'.format(excercise.id), {'reps': '5'}, follow=True)
        self.assertEqual(200, response.status_code)

        response = self.client.post('/add_reps/{}/'.format(excercise.id), {'reps': '5'}, follow=True)
        self.assertEqual(200, response.status_code)

        self.assertEqual(units.Volume(reps=20), workout.volume())
        self.assertEqual(20, statistics.total_reps())

        response = self.client.post('/finish_workout/{}'.format(workout.id), follow=True)
        self.assertEqual(200, response.status_code)

        statistics = self._expect_statistics_from_dashboard()
        workout = statistics.previous_workouts()[0]

        self.assertIsNotNone(workout.started)
        self.assertIsNotNone(workout.finished)
