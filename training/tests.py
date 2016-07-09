from django.test import TestCase, RequestFactory
from .models import TrainingSession, Excercise
from . import views


class TrainingSessionTestCase(TestCase):
    def setUp(self):
        self.session = TrainingSession.objects.create()

    def test_starting_session_should_mark_time_when_it_was_done(self):
        self.assertFalse(self.session.live())
        self.assertIsNone(self.session.started)

        self.session.start()

        self.assertTrue(self.session.live())
        self.assertIsNotNone(self.session.started)

    def test_session_cant_be_started_twice(self):
        self.session.start()
        with self.assertRaises(RuntimeError):
            self.session.start()

    def test_finishing_session_should_mark_the_time(self):
        self.session.start()

        self.assertIsNone(self.session.finished)

        self.session.finish()

        self.assertIsNotNone(self.session.started)
        self.assertIsNotNone(self.session.finished)

    def test_cant_finish_before_starting(self):
        with self.assertRaises(RuntimeError):
            self.session.finish()

    def test_cant_finish_twice(self):
        self.session.start()
        self.session.finish()
        with self.assertRaises(RuntimeError):
            self.session.finish()

    def test_cant_start_finished_session(self):
        self.session.start()
        self.session.finish()
        with self.assertRaises(RuntimeError):
            self.session.start()


class ViewsTestCase(TestCase):
    def setUp(self):
        self.request_factory = RequestFactory()

    def _start_workout(self):
        request = self.request_factory.get('')
        views.start_workout(request)

        # session gets started when first excercise starts
        session = TrainingSession.objects.get()
        self.assertFalse(session.live())

        return session

    def _finish_workout(self, session):
        request = self.request_factory.get('')
        views.finish_workout(request, session.pk)
        session.refresh_from_db()
        self.assertFalse(session.live())
        self.assertIsNotNone(session.started)
        self.assertIsNotNone(session.finished)

    def _start_excercise(self, session):
        request = self.request_factory.post('', {'name': "push-up"})
        views.add_excercise(request, session.pk)
        excercise = Excercise.objects.latest('pk')
        return excercise

    def _add_reps(self, excercise, reps):
        request = self.request_factory.post('', {'sets': reps})
        views.save_excercise(request, excercise.pk)
        excercise.refresh_from_db()
        self.assertEqual(reps, excercise.sets)

    def test_full_session(self):
        session = self._start_workout()

        push_ups = self._start_excercise(session)

        session.refresh_from_db()
        self.assertTrue(session.live())

        self._add_reps(push_ups, "10")
        self._add_reps(push_ups, "10 10")

        crunches = self._start_excercise(session)
        self._add_reps(crunches, "20")

        self._finish_workout(session)
