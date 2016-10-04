import datetime
import pytz
from decimal import Decimal

from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser, User

from training import models
from training.models import Workout, Excercise
from training import views


class ViewsTestCase(TestCase):
    def setUp(self):
        self.request_factory = RequestFactory()
        self.user = User.objects.create_user(username='jacob', email='jacob@…', password='top_secret')

    def _start_workout(self):
        request = self.request_factory.get('')
        request.user = self.user

        views.start_workout(request)

        # workout gets started when first excercise starts
        workout = Workout.objects.get()
        self.assertFalse(workout.live())

        return workout

    def _finish_workout(self, workout):
        request = self.request_factory.get('')
        request.user = self.user

        views.finish_workout(request, workout.pk)
        workout.refresh_from_db()
        self.assertFalse(workout.live())
        self.assertIsNotNone(workout.started)
        self.assertIsNotNone(workout.finished)

    def _start_excercise(self, workout):
        request = self.request_factory.post('', {'name': "push-up"})
        request.user = self.user
        views.add_excercise(request, workout.pk)
        excercise = Excercise.objects.latest('pk')
        return excercise

    def _add_reps(self, excercise, reps):
        request = self.request_factory.post('', {'reps': reps})
        request.user = self.user
        views.add_reps(request, excercise.pk)
        excercise.refresh_from_db()

    def test_full_session(self):
        workout = self._start_workout()

        push_ups = self._start_excercise(workout)

        workout.refresh_from_db()
        self.assertTrue(workout.live())

        self._add_reps(push_ups, "10")
        self._add_reps(push_ups, "10")

        self.assertEqual(20, sum(map(lambda x: x.reps, push_ups.reps_set.all())))

        crunches = self._start_excercise(workout)
        self._add_reps(crunches, "20")

        self._finish_workout(workout)


class ModelsTestCase(TestCase):
    def test_reps_most_common(self):
        user = User.objects.create_user(username='jacob', email='jacob@…', password='top_secret')
        workout = models.Workout.objects.create(user=user)

        excercise = workout.excercise_set.create()
        excercise.reps_set.create(reps=10)
        excercise.reps_set.create(reps=5)
        excercise.reps_set.create(reps=5)
        excercise.reps_set.create(reps=3)

        self.assertEqual([10, 5, 3], list(models.Reps.most_common()))
