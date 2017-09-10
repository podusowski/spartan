from contextlib import contextmanager
from unittest.mock import patch

from tests.utils import *
from tests import utils
from tests import test_strength
from training import units
from training import dates


@contextmanager
def faked_time(datetime):
    with patch('django.utils.timezone.now', autospec=True) as now:
        now.return_value = datetime
        yield


class StatisticsTestCase(ClientTestCase):
    _start_workout = utils.start_workout
    _strength_workout = utils.strength_workout
    _import_gpx = utils.import_gpx
    _timer_rep = test_strength._timer_rep

    def test_excercises_overview(self):
        self._import_gpx('3p_simplest.gpx')
        self._import_gpx('3p_simplest_2.gpx')
        self._import_gpx('running_no_points.gpx')

        self._import_gpx('3p_cycling.gpx')

        pushups = self._strength_workout('push-up', [2, 4, 8])
        more_pushups = self._strength_workout('push-up', [1])

        statistics = self.get('/statistics/statistics').context['statistics']
        excercises = statistics.most_popular_workouts()

        self.assertEqual('running', excercises[0].name)
        self.assertEqual(3, excercises[0].count)
        self.assertEqual(units.Volume(meters=8), excercises[0].volume)
        self.assertEqual(time(2016, 7, 30, 6, 22, 5), excercises[0].earliest)
        self.assertEqual(time(2016, 8, 30, 6, 22, 5), excercises[0].latest)

        self.assertEqual('push-up', excercises[1].name)
        self.assertEqual(2, excercises[1].count)
        self.assertEqual(units.Volume(reps=15), excercises[1].volume)
        self.assertEqual(pushups.started, excercises[1].earliest)
        self.assertEqual(more_pushups.started, excercises[1].latest)

        self.assertEqual('cycling', excercises[2].name)
        self.assertEqual(1, excercises[2].count)
        self.assertEqual(units.Volume(meters=4), excercises[2].volume)
        self.assertEqual(time(2016, 6, 30, 6, 22, 5), excercises[2].earliest)

    def test_timer_based_excercise_is_visible_on_statistics_page(self):
        workout = self._start_workout()

        self.post('/strength/add_excercise/{}/'.format(workout.id), {'name': 'plank front'})
        excercise = workout.excercise_set.latest('pk')

        self._timer_rep(excercise.id, ONE_O_CLOCK, TWO_O_CLOCK)

        statistics = self.get('/statistics/statistics').context['statistics']
        excercises = statistics.most_popular_workouts()

        self.assertEqual('plank front', excercises[0].name)
        #self.assertEqual(units.Volume(seconds=ONE_HOUR.total_seconds()), excercises[0].volume)
        self.assertEqual(1, excercises[0].count)

    def _get_workout_statistics(self, name, rng=None):
        if rng is None:
            return self.get('/statistics/workout/{}'.format(name)).context['workout']
        else:
            return self.get('/statistics/workout_during_timerange/{}/{}'.format(name, rng.tourl())).context['workout']

    def _find_statistics_field(self, name, field, rng=None):
        workout_statistics = dict(self._get_workout_statistics(name, rng))

        try:
            return workout_statistics[field]
        except KeyError as e:
            keys = ', '.join(["'{}'".format(k) for k in workout_statistics.keys()])
            raise KeyError("there is no '{}': it has: {}".format(field, keys))

    def test_workout_statistics_of_strength_workout(self):
        self.switch_user(self.other_user)

        self._strength_workout('push-up', [1])

        self.switch_user(self.user)

        self._strength_workout('push-up', [1, 2, 3])
        self._strength_workout('push-up', [2, 2])
        self._strength_workout('push-up', [10])

        self.assertEqual(3, self._find_statistics_field('push-up', 'total workouts'))
        assert self._find_statistics_field('push-up', 'total duration') is not None
        self.assertEqual(units.Volume(reps=20), self._find_statistics_field('push-up', 'total reps'))
        self.assertEqual(6, self._find_statistics_field('push-up', 'total series'))
        self.assertEqual(3, self._find_statistics_field('push-up', 'average reps per series'))
        self.assertEqual(7, self._find_statistics_field('push-up', 'average reps per workout'))

    def test_workout_statistics_of_strength_workout_max_reps(self):
        self._strength_workout('push-up', [5, 5, 5])
        self._strength_workout('push-up', [10])

        self.assertEqual(10, self._find_statistics_field('push-up', 'max reps per series'))
        self.assertEqual(15, self._find_statistics_field('push-up', 'max reps per workout'))

    def test_workout_statistics_of_gps_workout(self):
        self._import_gpx('3p_simplest.gpx')
        self._import_gpx('3p_simplest_2.gpx')

        self.assertEqual(2, self._find_statistics_field('running', 'total workouts'))
        self.assertEqual(datetime.timedelta(0, 4), self._find_statistics_field('running', 'total duration'))
        self.assertEqual(units.Volume(meters=8), self._find_statistics_field('running', 'total distance'))
        self.assertEqual(units.Volume(meters=4), self._find_statistics_field('running', 'average distance per workout'))
        self.assertEqual(units.Volume(meters=4), self._find_statistics_field('running', 'max distance'))

    def test_gps_statistics_in_timerange(self):
        self._import_gpx('3p_simplest.gpx')
        self._import_gpx('3p_simplest_2.gpx')

        rng = dates.TimeRange(time(2016, 8, 1, 0, 0, 0),
                              time(2016, 8, 31, 23, 59, 59, 999999))

        assert 1 == self._find_statistics_field('running', 'total workouts', rng)
        assert datetime.timedelta(0, 2) == self._find_statistics_field('running', 'total duration', rng)
        assert units.Volume(meters=4) == self._find_statistics_field('running', 'total distance', rng)
        assert units.Volume(meters=4) == self._find_statistics_field('running', 'average distance per workout', rng)
        assert units.Volume(meters=4) == self._find_statistics_field('running', 'max distance', rng)

    def test_strength_statistics_in_timerange(self):
        with faked_time(time(2016, 7, 1)):
            self._strength_workout('push-up', [5])

        with faked_time(time(2016, 8, 1)):
            self._strength_workout('push-up', [10])

        rng = dates.TimeRange(time(2016, 8, 1, 0, 0, 0),
                              time(2016, 8, 31, 23, 59, 59, 999999))

        assert 1 == self._find_statistics_field('push-up', 'total workouts', rng)
        assert self._find_statistics_field('push-up', 'total duration', rng) is not None
        assert units.Volume(reps=10) == self._find_statistics_field('push-up', 'total reps', rng)
        assert 1 == self._find_statistics_field('push-up', 'total series', rng)
        assert 10 == self._find_statistics_field('push-up', 'average reps per series', rng)
        assert 10 == self._find_statistics_field('push-up', 'average reps per workout', rng)
