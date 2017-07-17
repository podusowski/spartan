from unittest.mock import patch
from datetime import timedelta

from tests.utils import time, ClientTestCase
from tests import utils
from training import units


def _timer_rep(self, excercise_id, time_start, time_finished):
    with patch('django.utils.timezone.now', autospec=True) as now:
        now.return_value = time_start
        self.post('/strength/start_timer/{}'.format(excercise_id))

    with patch('django.utils.timezone.now', autospec=True) as now:
        now.return_value = time_finished
        self.post('/strength/stop_timer/{}'.format(excercise_id))


ONE_O_CLOCK = time(2016, 1, 1, 13, 0, 0)
TWO_O_CLOCK = time(2016, 1, 1, 14, 0, 0)
THREE_O_CLOCK = time(2016, 1, 1, 15, 0, 0)
FOUR_O_CLOCK = time(2016, 1, 1, 16, 0, 0)
ONE_HOUR = timedelta(hours=1)


class StrengthWorkoutTestCase(ClientTestCase):
    _strength_workout = utils.strength_workout
    _start_workout = utils.start_workout
    _timer_rep = _timer_rep

    def _view_workout(self, workout_id, status_code=200):
        return self.get('/workout/{}'.format(workout_id), status_code=status_code)

    def test_workout_can_be_viewed_after_starting(self):
        workout = self._start_workout()
        self._view_workout(workout.id)

    def test_strength_workout_type_when_starting_workout(self):
        workout = self._start_workout()
        self.assertEqual('strength', workout.workout_type)
        self.assertEqual('silver', workout.color)

    def test_finish_workout_without_any_excercise(self):
        workout = self._start_workout()

        with self.assertRaises(Exception):
            self.post('/strength/finish_workout/{}'.format(workout.id))

    def test_create_workout_and_delete_it(self):
        workout = self._start_workout()
        self.post('/delete_workout/{}/'.format(workout.id))

        self._view_workout(workout.id, status_code=404)

    def _get_statistics_from_dashboard(self):
        return self.get('/dashboard').context['statistics']

    def test_add_some_excercises_and_reps(self):
        workout = self._start_workout()

        self.assertIsNone(workout.started)
        self.assertIsNone(workout.finished)

        workout = self.post('/strength/add_excercise/{}/'.format(workout.id), {'name': 'push-up'}).context['workout']

        self.assertIsNotNone(workout.started)
        self.assertIsNone(workout.finished)

        excercise = workout.excercise_set.latest('pk')

        self.post('/strength/add_reps/{}/'.format(excercise.id), {'reps': '10'})
        self.post('/strength/add_excercise/{}/'.format(workout.id), {'name': 'pull-up'})

        excercise = workout.excercise_set.latest('pk')

        self.post('/strength/add_reps/{}/'.format(excercise.id), {'reps': '5'})
        self.post('/strength/add_reps/{}/'.format(excercise.id), {'reps': '5'})

        self.assertEqual(units.Volume(reps=20), workout.volume)
        self.assertEqual(units.Volume(reps=10), excercise.volume)

        workout = self.post('/strength/finish_workout/{}'.format(workout.id)).context['workout']

        self.assertIsNotNone(workout.started)
        self.assertIsNotNone(workout.finished)

    def test_timer_based_excercise(self):
        workout = self._start_workout()

        self.post('/strength/add_excercise/{}/'.format(workout.id), {'name': 'plank front'})
        excercise = workout.excercise_set.latest('pk')

        self._timer_rep(excercise.id, ONE_O_CLOCK, TWO_O_CLOCK)

        self.assertEqual(1, len(excercise.timers_set.all()))
        first_timer = excercise.timers_set.all()[0]

        self.assertEqual(ONE_O_CLOCK, first_timer.time_started)
        self.assertEqual(ONE_HOUR, first_timer.duration)

        self.assertEqual(units.Volume(seconds=ONE_HOUR.total_seconds()), workout.volume)

    def test_timer_mixed_with_reps_workout(self):
        workout = self._start_workout()

        self.post('/strength/add_excercise/{}/'.format(workout.id), {'name': 'plank front'})
        excercise = workout.excercise_set.latest('pk')
        self._timer_rep(excercise.id, ONE_O_CLOCK, TWO_O_CLOCK)

        self.post('/strength/add_excercise/{}/'.format(workout.id), {'name': 'push-up'})
        excercise = workout.excercise_set.latest('pk')
        self.post('/strength/add_reps/{}/'.format(excercise.id), {'reps': '2'})
        self.post('/strength/add_reps/{}/'.format(excercise.id), {'reps': '1'})

        self.assertEqual(units.MultiVolume([units.Volume(seconds=ONE_HOUR.total_seconds()),
                                            units.Volume(reps=3)]),
                         workout.volume)

    def test_undo_last_rep(self):
        workout = self._start_workout()

        self.post('/strength/add_excercise/{}/'.format(workout.id), {'name': 'push-up'})
        excercise = workout.excercise_set.latest('pk')

        self.post('/strength/add_reps/{}/'.format(excercise.id), {'reps': '2'})
        self.post('/strength/add_reps/{}/'.format(excercise.id), {'reps': '3'})
        self.assertEqual(units.Volume(reps=5), workout.volume)

        self.post('/strength/undo/{}'.format(workout.id))
        self.assertEqual(units.Volume(reps=2), workout.volume)

    def test_undo_last_excercise(self):
        workout = self._start_workout()

        self.post('/strength/add_excercise/{}/'.format(workout.id), {'name': 'push-up'})
        self.assertEqual(1, workout.excercise_set.count())

        self.post('/strength/undo/{}'.format(workout.id))
        self.assertEqual(0, workout.excercise_set.count())

    def test_undo_does_nothing_where_there_is_nothing_to_do(self):
        workout = self._start_workout()
        self.post('/strength/undo/{}'.format(workout.id))
        self.assertEqual(0, workout.excercise_set.count())

    def _pushups(self, series):
        return self._strength_workout('push-up', series)

    def test_most_common_reps(self):
        statistics = self._get_statistics_from_dashboard()

        self.assertEqual([], list(statistics.most_common_reps()))

        self._pushups([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        self.assertEqual([10, 9, 8], list(statistics.most_common_reps(3)))

        self._pushups([11])
        self.assertEqual([11, 10, 9], list(statistics.most_common_reps(3)))

        self._pushups([10, 10, 10])
        self.assertEqual([11, 10, 9], list(statistics.most_common_reps(3)))

        self._pushups([1, 1, 1])
        self.assertEqual([11, 10, 1], list(statistics.most_common_reps(3)))


class StatisticsTestCase(ClientTestCase):
    _start_workout = utils.start_workout
    _timer_rep = _timer_rep

    def _get_statistics_from_dashboard(self):
        return self.get('/dashboard').context['statistics']

    def test_timer_based_excercise_is_visible_on_statistics_page(self):
        workout = self._start_workout()

        self.post('/strength/add_excercise/{}/'.format(workout.id), {'name': 'plank front'})
        excercise = workout.excercise_set.latest('pk')

        self._timer_rep(excercise.id, ONE_O_CLOCK, TWO_O_CLOCK)

        statistics = self._get_statistics_from_dashboard()
        excercises = statistics.most_popular_workouts()

        self.assertEqual('plank front', excercises[0].name)
        #self.assertEqual(units.Volume(seconds=ONE_HOUR.total_seconds()), excercises[0].volume)
        self.assertEqual(1, excercises[0].count)

    def test_timer_based_excercise_with_two_reps(self):
        workout = self._start_workout()

        self.post('/strength/add_excercise/{}/'.format(workout.id), {'name': 'plank front'})
        excercise = workout.excercise_set.latest('pk')

        self._timer_rep(excercise.id, ONE_O_CLOCK, TWO_O_CLOCK)
        self._timer_rep(excercise.id, THREE_O_CLOCK, FOUR_O_CLOCK)

        self.assertEqual(2, len(excercise.timers_set.all()))
        second_timer = excercise.timers_set.all()[1]

        self.assertEqual(THREE_O_CLOCK, second_timer.time_started)
        self.assertEqual(ONE_HOUR, second_timer.duration)

