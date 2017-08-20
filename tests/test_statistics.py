from tests.utils import *
from tests import utils
from training import units

from tests import test_strength


class StatisticsTestCase(ClientTestCase):
    _start_workout = utils.start_workout
    _strength_workout = utils.strength_workout
    _import_gpx = utils.import_gpx
    _timer_rep = test_strength._timer_rep

    def _get_statistics_from_dashboard(self):
        return self.get('/dashboard').context['statistics']

    def test_most_popular_excercises(self):
        self._import_gpx('3p_simplest.gpx')
        self._import_gpx('3p_simplest_2.gpx')
        self._import_gpx('running_no_points.gpx')

        self._import_gpx('3p_cycling.gpx')

        pushups = self._strength_workout('push-up', [2, 4, 8])
        more_pushups = self._strength_workout('push-up', [1])

        statistics = self._get_statistics_from_dashboard()
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

        statistics = self._get_statistics_from_dashboard()
        excercises = statistics.most_popular_workouts()

        self.assertEqual('plank front', excercises[0].name)
        #self.assertEqual(units.Volume(seconds=ONE_HOUR.total_seconds()), excercises[0].volume)
        self.assertEqual(1, excercises[0].count)

    def _get_workout_statistics(self, name):
        return self.get('/statistics/workout/{}'.format(name)).context['workout']

    def _find_statistics_field(self, name, field):
        workout_statistics = self._get_workout_statistics(name)
        metrics = workout_statistics.metrics()
        return dict(metrics)[field]

    def test_strength_statistics(self):
        self.switch_user(self.other_user)

        self._strength_workout('push-up', [1])

        self.switch_user(self.user)

        self._strength_workout('push-up', [1, 2, 3])
        self._strength_workout('push-up', [2, 2])
        self._strength_workout('push-up', [10])

        self.assertEqual(3, self._find_statistics_field('push-up', 'total workouts'))
        self.assertEqual(units.Volume(reps=20), self._find_statistics_field('push-up', 'total reps'))
        self.assertEqual(6, self._find_statistics_field('push-up', 'total series'))
        self.assertEqual(3, self._find_statistics_field('push-up', 'average reps per series'))
        self.assertEqual(7, self._find_statistics_field('push-up', 'average reps per workout'))

    def test_strength_max(self):
        self._strength_workout('push-up', [5, 5, 5])
        self._strength_workout('push-up', [10])

        self.assertEqual(10, self._find_statistics_field('push-up', 'max reps per series'))
        self.assertEqual(15, self._find_statistics_field('push-up', 'max reps per workout'))

    def test_gps_statistics(self):
        self._import_gpx('3p_simplest.gpx')
        self._import_gpx('3p_simplest_2.gpx')

        self.assertEqual(2, self._find_statistics_field('running', 'total workouts'))
        self.assertEqual(units.Volume(meters=8), self._find_statistics_field('running', 'total distance'))
        self.assertEqual(units.Volume(meters=4), self._find_statistics_field('running', 'average distance per workout'))
        self.assertEqual(units.Volume(meters=4), self._find_statistics_field('running', 'max distance'))
