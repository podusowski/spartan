from django.test import Client, TestCase
from django.contrib.auth.models import User

from training import models


class ClienStrengthTestCase(TestCase):
    def test_create_workout(self):
        user = User.objects.create_user(username='grzegorz', email='', password='z')

        c = Client()
        response = c.post('/login/', {'username': 'grzegorz', 'password': 'z'})
        self.assertEqual(302, response.status_code)
        self.assertEqual('/dashboard', response['Location'])

        # no workouts yet
        self.assertEqual(0, len(models.Workout.objects.all()))

        response = c.get('/start_workout', follow=True)
        self.assertEqual(200, response.status_code)
        self.assertIsNotNone(response.context['workout'])

        workout_id = response.context['workout'].id

        response = c.post('/add_excercise/{}/'.format(workout_id), {'name': 'push-up'}, follow=True)
        self.assertEqual(200, response.status_code)

        self.assertEqual(1, len(models.Workout.objects.all()))

        response = c.post('/finish_workout/{}/'.format(workout_id), follow=True)

        self.assertEqual(1, len(models.Workout.objects.all()))

        response = c.post('/delete_workout/{}/'.format(workout_id), follow=True)

        self.assertEqual(0, len(models.Workout.objects.all()))
