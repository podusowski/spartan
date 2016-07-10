from django.test import TestCase, RequestFactory
from .models import Workout, Excercise
from . import views


class TrainingSessionTestCase(TestCase):
    def setUp(self):
        self.workout = Workout.objects.create()

    def test_starting_session_should_mark_time_when_it_was_done(self):
        self.assertFalse(self.workout.live())
        self.assertIsNone(self.workout.started)

        self.workout.start()

        self.assertTrue(self.workout.live())
        self.assertIsNotNone(self.workout.started)

    def test_session_cant_be_started_twice(self):
        self.workout.start()
        with self.assertRaises(RuntimeError):
            self.workout.start()

    def test_finishing_session_should_mark_the_time(self):
        self.workout.start()

        self.assertIsNone(self.workout.finished)

        self.workout.finish()

        self.assertIsNotNone(self.workout.started)
        self.assertIsNotNone(self.workout.finished)

    def test_cant_finish_before_starting(self):
        with self.assertRaises(RuntimeError):
            self.workout.finish()

    def test_cant_finish_twice(self):
        self.workout.start()
        self.workout.finish()
        with self.assertRaises(RuntimeError):
            self.workout.finish()

    def test_cant_start_finished_session(self):
        self.workout.start()
        self.workout.finish()
        with self.assertRaises(RuntimeError):
            self.workout.start()


class ViewsTestCase(TestCase):
    def setUp(self):
        self.request_factory = RequestFactory()

    def _start_workout(self):
        request = self.request_factory.get('')
        views.start_workout(request)

        # workout gets started when first excercise starts
        workout = Workout.objects.get()
        self.assertFalse(workout.live())

        return workout

    def _finish_workout(self, workout):
        request = self.request_factory.get('')
        views.finish_workout(request, workout.pk)
        workout.refresh_from_db()
        self.assertFalse(workout.live())
        self.assertIsNotNone(workout.started)
        self.assertIsNotNone(workout.finished)

    def _start_excercise(self, workout):
        request = self.request_factory.post('', {'name': "push-up"})
        views.add_excercise(request, workout.pk)
        excercise = Excercise.objects.latest('pk')
        return excercise

    def _add_reps(self, excercise, reps):
        request = self.request_factory.post('', {'reps': reps})
        views.add_reps(request, excercise.pk, reps)
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
