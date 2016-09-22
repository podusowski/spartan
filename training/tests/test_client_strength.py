from django.test import Client, TestCase
from django.contrib.auth.models import User

from training import models


class ClienStrengthTestCase(TestCase):
    def setUp(self):
        user = User.objects.create_user(username='grzegorz', email='', password='z')
        self.client = Client()

    def _expect_accessible_workout_page(self, workout_id):
        response = self.client.get('/workout/{}'.format(workout_id), follow=True)
        self.assertEqual(200, response.status_code)

    def test_create_workout(self):
        response = self.client.post('/login/', {'username': 'grzegorz', 'password': 'z'})
        self.assertEqual(302, response.status_code)
        self.assertEqual('/dashboard', response['Location'])

        # no workouts yet
        self.assertEqual(0, len(models.Workout.objects.all()))

        response = self.client.get('/start_workout', follow=True)
        self.assertEqual(200, response.status_code)
        self.assertIsNotNone(response.context['workout'])

        workout_id = response.context['workout'].id

        self._expect_accessible_workout_page(workout_id)

        response = self.client.post('/add_excercise/{}/'.format(workout_id), {'name': 'push-up'}, follow=True)
        self.assertEqual(200, response.status_code)

        self._expect_accessible_workout_page(workout_id)

        response = self.client.post('/finish_workout/{}'.format(workout_id), follow=True)
        self.assertEqual(200, response.status_code)

        self._expect_accessible_workout_page(workout_id)

        response = self.client.post('/delete_workout/{}/'.format(workout_id), follow=True)
        self.assertEqual(200, response.status_code)

        self.assertEqual(0, len(models.Workout.objects.all()))
