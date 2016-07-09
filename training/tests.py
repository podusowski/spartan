from django.test import TestCase
from .models import TrainingSession


class TrainingSessionTestCase(TestCase):
    def test_starting_session_should_mark_time_when_it_was_done(self):
        session = TrainingSession.objects.create()

        self.assertFalse(session.live())
        self.assertIsNone(session.started)

        session.start()

        self.assertTrue(session.live())
        self.assertIsNotNone(session.started)

    def test_session_cant_be_started_twice(self):
        session = TrainingSession.objects.create()

        session.start()
        with self.assertRaises(RuntimeError):
            session.start()
