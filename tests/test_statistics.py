from tests.utils import time, ClientTestCase
from tests import utils
from training import units


class StatisticsTestCase(ClientTestCase):
    _strength_workout = utils.strength_workout
    _import_gpx = utils.import_gpx

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
