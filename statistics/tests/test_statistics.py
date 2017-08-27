import datetime
import pytz
from unittest.mock import patch, Mock, PropertyMock

from training import models, units
from statistics import statistics
from statistics import goals

from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.http import Http404


FIRST_SEPT_2016 = datetime.datetime(2016, 9, 1, 0, 0, 0, tzinfo=pytz.utc)
SECOND_SEPT_2016 = datetime.datetime(2016, 9, 2, 0, 0, 0, tzinfo=pytz.utc)


class StatisticsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='jacob',
                                             email='jacob@…',
                                             password='top_secret')

        self.other_user = User.objects.create_user(username='zysz',
                                                   email='jacob@…',
                                                   password='top_secret')

        self.statistics = statistics.Statistics(self.user)

    def test_weeks(self):
        models.Workout.objects.create(user=self.user,
                                      activity_type='test',
                                      started=FIRST_SEPT_2016,
                                      finished=datetime.datetime(2016, 9, 1, 0, 0, 1, tzinfo=pytz.utc))

        models.Workout.objects.create(user=self.other_user,
                                      activity_type='test',
                                      started=FIRST_SEPT_2016,
                                      finished=datetime.datetime(2016, 9, 1, 0, 0, 1, tzinfo=pytz.utc))

        weeks = self.statistics.weeks(start=datetime.datetime(2016, 9, 4, 23, 59, 59))

        self.assertEqual(1, len(weeks))
        self.assertEqual(1, len(weeks[0].workouts))

        days = list(weeks[0].days)
        self.assertEqual(1, len(days[3].workouts)) # thursday

    def test_create_goal(self):
        user_goals = goals.Goals(self.user)
        user_goals.set("push-up", 100)
        user_goals.set("sit-up", 200)
        user_goals.set("push-up", 50)

        other_user_goals = goals.Goals(self.other_user)
        other_user_goals.set("push-up", 1000)

        self.assertEqual([50, 200], [g.volume for g in user_goals.all()])

    def test_getting_goal_by_name(self):
        user_goals = goals.Goals(self.user)
        user_goals.set("push-up", 100)
        goal = user_goals.get("push-up")

        self.assertEqual(100, goal.volume)

    def test_delete_goal(self):
        user_goals = goals.Goals(self.user)
        user_goals.set("push-up", 100)

        other_user_goals = goals.Goals(self.other_user)
        other_user_goals.set("push-up", 1000)

        self.assertEqual(1, len(user_goals.all()))

        user_goals.delete("push-up")

        self.assertEqual(1, len(other_user_goals.all()))
        self.assertEqual(0, len(user_goals.all()))

    def test_goal_properties(self):
        with patch('statistics.goals.Statistics', autospec=True) as StatisticsMock:
            statistics_mock = StatisticsMock.return_value

            user_goals = goals.Goals(self.user)
            user_goals.set('push-up', 3)

            push_ups = statistics.PopularWorkout(name='push-up', count=1, volume=units.Volume(reps=0), earliest=None, latest=None)
            statistics_mock.favourites_this_month.return_value = [push_ups]
            all_goals = user_goals.all()
            self.assertEqual(units.Volume(0), all_goals[0].progress)
            self.assertEqual(0, all_goals[0].percent)

            other_push_ups = statistics.PopularWorkout(name='push-up', count=1, volume=units.Volume(reps=1), earliest=None, latest=None)
            statistics_mock.favourites_this_month.return_value = [other_push_ups]
            all_goals = user_goals.all()
            self.assertEqual(units.Volume(reps=1), all_goals[0].progress)
            self.assertEqual(33, all_goals[0].percent)

    def test_workouts_without_goal(self):
        with patch('statistics.goals.Statistics', autospec=True) as StatisticsMock:
            statistics_mock = StatisticsMock.return_value

            user_goals = goals.Goals(self.user)
            user_goals.set('push-up', 3)

            push_ups = statistics.PopularWorkout(name='push-up', count=1, volume=units.Volume(reps=1), earliest=None, latest=None)
            running = statistics.PopularWorkout(name='running', count=1, volume=units.Volume(meters=1), earliest=None, latest=None)

            statistics_mock.most_popular_workouts.return_value = [push_ups, running]

            self.assertEqual(['running'], user_goals.workouts_not_having_goal())
