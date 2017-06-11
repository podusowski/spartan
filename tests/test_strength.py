from unittest.mock import patch

from tests.utils import time, ClientTestCase
from training import units


class StrengthWorkoutTestCase(ClientTestCase):
    def _strength_workout(self, name, series):
        workout = self._start_workout()

        self.post('/strength/add_excercise/{}/'.format(workout.id), {'name': name})

        excercise = workout.excercise_set.latest('pk')

        for reps in series:
            self.post('/strength/add_reps/{}/'.format(excercise.id), {'reps': reps})

        return self.post('/strength/finish_workout/{}'.format(workout.id)).context['workout']

    def _start_workout(self):
        workout = self.get('/strength/start_workout').context['workout']
        self._view_workout(workout.id)
        return workout

    def _view_workout(self, workout_id, status_code=200):
        return self.get('/workout/{}'.format(workout_id), status_code=status_code)

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
        self._start_workout()

        statistics = self._get_statistics_from_dashboard()
        workout = statistics.previous_workouts()[0]

        self.assertIsNone(workout.started)
        self.assertIsNone(workout.finished)

        self.post('/strength/add_excercise/{}/'.format(workout.id), {'name': 'push-up'})

        statistics = self._get_statistics_from_dashboard()
        workout = statistics.previous_workouts()[0]

        self.assertIsNotNone(workout.started)
        self.assertIsNone(workout.finished)

        excercise = workout.excercise_set.latest('pk')

        self.post('/strength/add_reps/{}/'.format(excercise.id), {'reps': '10'})
        self.post('/strength/add_excercise/{}/'.format(workout.id), {'name': 'pull-up'})

        excercise = workout.excercise_set.latest('pk')

        self.post('/strength/add_reps/{}/'.format(excercise.id), {'reps': '5'})
        self.post('/strength/add_reps/{}/'.format(excercise.id), {'reps': '5'})

        self.assertEqual(units.Volume(reps=20), workout.volume())

        self.post('/strength/finish_workout/{}'.format(workout.id))

        statistics = self._get_statistics_from_dashboard()
        workout = statistics.previous_workouts()[0]

        self.assertIsNotNone(workout.started)
        self.assertIsNotNone(workout.finished)

    ONE_O_CLOCK = time(2016, 1, 1, 13, 0, 0)
    TWO_O_CLOCK = time(2016, 1, 1, 14, 0, 0)
    THREE_O_CLOCK = time(2016, 1, 1, 15, 0, 0)
    FOUR_O_CLOCK = time(2016, 1, 1, 16, 0, 0)

    def _timer_rep(self, excercise_id, time_start, time_finished):
        with patch('django.utils.timezone.now', autospec=True) as now:
            now.return_value = time_start
            self.post('/strength/start_timer/{}'.format(excercise_id))

        with patch('django.utils.timezone.now', autospec=True) as now:
            now.return_value = time_finished
            self.post('/strength/stop_timer/{}'.format(excercise_id))

    def test_timer_based_excercise(self):
        self._start_workout()

        statistics = self._get_statistics_from_dashboard()
        workout = statistics.previous_workouts()[0]

        self.post('/strength/add_excercise/{}/'.format(workout.id), {'name': 'plank front'})
        excercise = workout.excercise_set.latest('pk')

        self._timer_rep(excercise.id, self.ONE_O_CLOCK, self.TWO_O_CLOCK)

        self.assertEqual(1, len(excercise.timers_set.all()))
        first_timer = excercise.timers_set.all()[0]

        self.assertEqual(self.ONE_O_CLOCK, first_timer.time_started)
        self.assertEqual(self.TWO_O_CLOCK, first_timer.time_finished)

        statistics = self._get_statistics_from_dashboard()
        excercises = statistics.most_popular_workouts()

        self.assertEqual('plank front', excercises[0].name)
        self.assertEqual(1, excercises[0].count)
        #self.assertEqual(units.Volume(seconds=15), excercises[0].volume)
        #self.assertEqual(pushups.started, excercises[1].earliest)
        #self.assertEqual(more_pushups.started, excercises[1].latest)

    def test_timer_based_excercise_with_two_reps(self):
        self._start_workout()

        statistics = self._get_statistics_from_dashboard()
        workout = statistics.previous_workouts()[0]

        self.post('/strength/add_excercise/{}/'.format(workout.id), {'name': 'plank front'})
        excercise = workout.excercise_set.latest('pk')

        self._timer_rep(excercise.id, self.ONE_O_CLOCK, self.TWO_O_CLOCK)
        self._timer_rep(excercise.id, self.THREE_O_CLOCK, self.FOUR_O_CLOCK)

        self.assertEqual(2, len(excercise.timers_set.all()))
        second_timer = excercise.timers_set.all()[1]

        self.assertEqual(self.THREE_O_CLOCK, second_timer.time_started)
        self.assertEqual(self.FOUR_O_CLOCK, second_timer.time_finished)

    def test_undo_last_rep(self):
        workout = self._start_workout()

        self.post('/strength/add_excercise/{}/'.format(workout.id), {'name': 'push-up'})
        excercise = workout.excercise_set.latest('pk')

        self.post('/strength/add_reps/{}/'.format(excercise.id), {'reps': '2'})
        self.post('/strength/add_reps/{}/'.format(excercise.id), {'reps': '3'})
        self.assertEqual(units.Volume(reps=5), workout.volume())

        self.post('/strength/undo/{}'.format(workout.id))
        self.assertEqual(units.Volume(reps=2), workout.volume())

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

    def _do_some_pushups(self, series):
        return self._strength_workout('push-up', series)

    def test_most_common_reps(self):
        statistics = self._get_statistics_from_dashboard()

        self.assertEqual([], list(statistics.most_common_reps()))

        self._do_some_pushups([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        self.assertEqual([10, 9, 8], list(statistics.most_common_reps(3)))

        self._do_some_pushups([11])
        self.assertEqual([11, 10, 9], list(statistics.most_common_reps(3)))

        self._do_some_pushups([10, 10, 10])
        self.assertEqual([11, 10, 9], list(statistics.most_common_reps(3)))

        self._do_some_pushups([1, 1, 1])
        self.assertEqual([11, 10, 1], list(statistics.most_common_reps(3)))
