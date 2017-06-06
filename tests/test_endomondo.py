import datetime
import unittest.mock
from unittest.mock import patch, Mock

from tests.utils import time, ClientTestCase


class EndomondoTestCase(ClientTestCase):
    def _get_statistics_from_dashboard(self):
        return self.get('/dashboard').context['statistics']

    def test_connect_to_endomondo(self):
        with patch('endoapi.endomondo.Endomondo') as endomondo:
            endomondo_mock = Mock()
            endomondo.return_value = endomondo_mock
            endomondo.return_value.token = 'token'

            key = self.get('/gps/endomondo/').context['key']
            self.assertIsNone(key)

            self.post('/gps/endomondo/', {'email': 'legan@com.pl', 'password': 'haslo'})
            endomondo.assert_called_with(email='legan@com.pl', password='haslo')

            key = self.get('/gps/endomondo/').context['key']
            self.assertEqual('token', key.key)

            key = self.get('/gps/disconnect_endomondo/').context['key']
            self.assertIsNone(key)

    def test_import_from_endomondo_no_workouts(self):
        with patch('endoapi.endomondo.Endomondo', autospec=True) as endomondo:
            endomondo.return_value = Mock()
            endomondo.return_value.token = 'token'

            self.post('/gps/endomondo/', {'email': 'legan@com.pl', 'password': 'haslo'})

            endomondo.return_value.fetch.return_value = []
            self.get('/gps/synchronize_endomondo_ajax/')

            endomondo.return_value.fetch.assert_called_once_with(max_results=10, before=None, after=None)

            statistics = self._get_statistics_from_dashboard()
            self.assertEqual(0, len(statistics.previous_workouts()))

    def test_import_many_workouts_from_endomondo(self):

        def make_endomondo_workout(i):

            class EndomondoWorkout:
                pass

            workout = EndomondoWorkout()
            workout.id = i
            workout.sport = "running"
            workout.distance = 10
            workout.start_time = time(2016, 1, 1, 0, 0, 0)
            workout.duration = datetime.timedelta(seconds=i)
            workout.points = []

            return workout

        with patch('endoapi.endomondo.Endomondo', autospec=True) as endomondo:
            endomondo.return_value = Mock()
            endomondo.return_value.token = 'token'

            self.post('/gps/endomondo/', {'email': 'legan@com.pl', 'password': 'haslo'})

            endomondo.return_value.fetch.return_value = [make_endomondo_workout(i) for i in range(10)]
            self.get('/gps/synchronize_endomondo_ajax/')

            endomondo.return_value.fetch.assert_called_once_with(max_results=10, before=None, after=None)

            statistics = self._get_statistics_from_dashboard()
            self.assertEqual(10, len(statistics.previous_workouts()))
