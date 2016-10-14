import os
import pytz
import datetime

from django.test import Client, TestCase


GPX_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gpx')


def time(y, month, d, h=0, m=0, s=0, ms=0):
    return datetime.datetime(y, month, d, h, m, s, ms, tzinfo=pytz.utc)


class ClientTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def get(self, uri, status_code=200):
        response = self.client.get(uri, follow=True)
        self.assertEqual(status_code, response.status_code)
        return response

    def post(self, uri, data={}, status_code=200):
        response = self.client.post(uri, data, follow=True)
        self.assertEqual(status_code, response.status_code)
        return response
