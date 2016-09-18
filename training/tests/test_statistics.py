import datetime
import pytz

from training import models
import training.statistics
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User


class StatisticsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='jacob',
                                             email='jacob@…',
                                             password='top_secret')

    def test_weeks(self):
        models.Workout.objects.create(user=self.user,
                                      started=datetime.datetime(2016, 9, 1, 0, 0, 0, tzinfo=pytz.utc),
                                      finished=datetime.datetime(2016, 9, 1, 0, 0, 1, tzinfo=pytz.utc))

        statistics = training.statistics.Statistics(self.user)
        weeks = statistics.weeks(start=datetime.datetime(2016, 9, 4, 23, 59, 59))

        self.assertEqual(1, len(weeks))
        self.assertEqual(1, len(weeks[0].workouts))

        days = list(weeks[0].days)
        self.assertEqual(1, len(days[3].workouts)) # thursday

    def test_most_popular_workout_types(self):
        models.Workout.objects.create(user=self.user,
                                      workout_type="strength",
                                      started=datetime.datetime(2016, 9, 1, 0, 0, 0, tzinfo=pytz.utc),
                                      finished=datetime.datetime(2016, 9, 1, 0, 0, 1, tzinfo=pytz.utc))

        models.Workout.objects.create(user=self.user,
                                      workout_type="strength",
                                      started=datetime.datetime(2016, 9, 2, 0, 0, 0, tzinfo=pytz.utc),
                                      finished=datetime.datetime(2016, 9, 2, 0, 0, 1, tzinfo=pytz.utc))

        models.Workout.objects.create(user=self.user,
                                      workout_type="pilates",
                                      started=datetime.datetime(2016, 9, 3, 0, 0, 0, tzinfo=pytz.utc),
                                      finished=datetime.datetime(2016, 9, 3, 0, 0, 1, tzinfo=pytz.utc))

        statistics = training.statistics.Statistics(self.user)

        most_popular_workouts = statistics.most_popular_workouts()
        self.assertEqual(2, len(most_popular_workouts))
        self.assertEqual(("strength", 2), most_popular_workouts[0])
        self.assertEqual(("pilates", 1), most_popular_workouts[1])
