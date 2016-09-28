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

        self.statistics = training.statistics.Statistics(self.user)

    def test_weeks(self):
        models.Workout.objects.create(user=self.user,
                                      started=datetime.datetime(2016, 9, 1, 0, 0, 0, tzinfo=pytz.utc),
                                      finished=datetime.datetime(2016, 9, 1, 0, 0, 1, tzinfo=pytz.utc))

        weeks = self.statistics.weeks(start=datetime.datetime(2016, 9, 4, 23, 59, 59))

        self.assertEqual(1, len(weeks))
        self.assertEqual(1, len(weeks[0].workouts))

        days = list(weeks[0].days)
        self.assertEqual(1, len(days[3].workouts)) # thursday

    def _create_gpx_workout(self, time_started, time_finished, activity_type):
        workout = models.Workout.objects.create(user=self.user,
                                                started=time_started,
                                                finished=time_finished)

        models.Gpx.objects.create(workout=workout,
                                  activity_type=activity_type)

    def test_most_popular_workout_types(self):
        self._create_gpx_workout(time_started=datetime.datetime(2016, 9, 1, 0, 0, 0, tzinfo=pytz.utc),
                                 time_finished=datetime.datetime(2016, 9, 1, 0, 0, 1, tzinfo=pytz.utc),
                                 activity_type='strength')

        self._create_gpx_workout(time_started=datetime.datetime(2016, 9, 2, 0, 0, 0, tzinfo=pytz.utc),
                                 time_finished=datetime.datetime(2016, 9, 2, 0, 0, 1, tzinfo=pytz.utc),
                                 activity_type='strength')

        self._create_gpx_workout(time_started=datetime.datetime(2016, 9, 3, 0, 0, 0, tzinfo=pytz.utc),
                                 time_finished=datetime.datetime(2016, 9, 3, 0, 0, 1, tzinfo=pytz.utc),
                                 activity_type='pilates')

        most_popular_workouts = list(self.statistics.most_popular_workouts())
        self.assertEqual(2, len(most_popular_workouts))
        self.assertEqual(("strength", 2, 0), most_popular_workouts[0])
        self.assertEqual(("pilates", 1, 0), most_popular_workouts[1])
