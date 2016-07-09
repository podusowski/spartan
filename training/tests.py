from django.test import TestCase
from .models import TrainingSession
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
    pass
