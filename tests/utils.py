import os
import pytz
import datetime

from django.contrib.auth.models import User
from django.test import Client, TestCase


def time(y, month, d, h=0, m=0, s=0, ms=0):
    return datetime.datetime(y, month, d, h, m, s, ms, tzinfo=pytz.utc)


ONE_O_CLOCK = time(2016, 1, 1, 13, 0, 0)
TWO_O_CLOCK = time(2016, 1, 1, 14, 0, 0)
THREE_O_CLOCK = time(2016, 1, 1, 15, 0, 0)
FOUR_O_CLOCK = time(2016, 1, 1, 16, 0, 0)
ONE_HOUR = datetime.timedelta(hours=1)


class ClientTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='grzegorz', email='', password='z')
        self.other_user = User.objects.create_user(username='other', email='', password='z')

        self.post('/login/', {'username': 'grzegorz', 'password': 'z'})

    def switch_user(self, user):
        self.get('/logout/')
        self.post('/login/', {'username': user.username, 'password': 'z'})

    def get(self, uri, status_code=200):
        response = self.client.get(uri, follow=True)
        self.assertEqual(status_code, response.status_code)
        return response

    def post(self, uri, data={}, status_code=200):
        response = self.client.post(uri, data, follow=True)
        self.assertEqual(status_code, response.status_code)
        return response


def start_workout(self):
    workout = self.get('/strength/start_workout').context['workout']
    return workout


def strength_workout(self, name, series):
    workout = start_workout(self)

    self.post('/strength/add_excercise/{}/'.format(workout.id), {'name': name})

    excercise = workout.excercise_set.latest('pk')

    for reps in series:
        self.post('/strength/add_reps/{}/'.format(excercise.id), {'reps': reps})

    return self.post('/strength/finish_workout/{}'.format(workout.id)).context['workout']


GPX_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gpx')


def import_gpx(self, filename):
    path = os.path.join(GPX_DIR, filename)
    with open(path, 'r') as f:
        return self.post('/gps/upload_gpx/', {'gpxfile': f}).context['workout']
