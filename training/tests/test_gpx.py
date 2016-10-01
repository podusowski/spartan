import os
import datetime
import pytz
import json
from decimal import Decimal

from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import AnonymousUser, User
from django.test import TestCase, RequestFactory

from training import gpx
from training import models


class GpxTestCase(TestCase):
    def setUp(self):
        self.request_factory = RequestFactory()
        self.request = self.request_factory.get('')
        self.user = User.objects.create_user(username='jacob', email='jacob@…', password='top_secret')
        self.request.user = self.user

    def _make_simple_upload_file(self, filename):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        GPX_FILE = os.path.join(BASE_DIR, filename)
        return SimpleUploadedFile('workout.gpx', open(GPX_FILE, 'rb').read())

    def test_make_sure_basic_stuff_is_imported_from_gpx(self):
        self.request.FILES['gpxfile'] = self._make_simple_upload_file("3p_simplest.gpx")

        gpx.upload_gpx(self.request)

        workout = models.Workout.objects.get()
        self.assertTrue(workout.is_gpx());
        self.assertEqual(datetime.datetime(2016, 7, 30, 6, 22, 5, tzinfo=pytz.utc), workout.started)
        self.assertEqual(datetime.datetime(2016, 7, 30, 6, 22, 7, tzinfo=pytz.utc), workout.finished)

        gpx_workout = workout.gpx_set.get()
        self.assertEqual("RUNNING", gpx_workout.activity_type)
        self.assertEqual(4, gpx_workout.distance)

    def test_exporting_gpx_points_as_json(self):
        self.request.FILES['gpxfile'] = self._make_simple_upload_file("3p_hr_cad.gpx")

        gpx.upload_gpx(self.request)

        workout = models.Workout.objects.get()
        gpx_workout = workout.gpx_set.get()

        expected_points = [{'lat': 51.05772623, 'lon': 16.99809956, 'hr': 100, 'cad': 60,
			    'time': datetime.datetime(2016, 7, 30, 6, 22, 5, tzinfo=pytz.utc).isoformat()},
                           {'lat': 51.05773386, 'lon': 16.99807215, 'hr': 110, 'cad': 70,
			    'time': datetime.datetime(2016, 7, 30, 6, 22, 6, tzinfo=pytz.utc).isoformat()},
                           {'lat': 51.05774031, 'lon': 16.99804198, 'hr': 120, 'cad': 80,
                            'time': datetime.datetime(2016, 7, 30, 6, 22, 7, tzinfo=pytz.utc).isoformat()}]

        self.assertEqual(expected_points, json.loads(gpx_workout.points_as_json()))

    def test_calculation_of_average_heart_rate_and_cadence(self):
        self.request.FILES['gpxfile'] = self._make_simple_upload_file("3p_hr_cad.gpx")

        gpx.upload_gpx(self.request)

        workout = models.Workout.objects.get()
        gpx_workout = workout.gpx_set.get()

        self.assertEqual(110, gpx_workout.average_hr())
        self.assertEqual(70, gpx_workout.average_cad())

    def test_calculation_of_average_heart_rate_and_cadence_if_gpx_is_without_meas(self):
        self.request.FILES['gpxfile'] = self._make_simple_upload_file("3p_simplest.gpx")

        gpx.upload_gpx(self.request)

        workout = models.Workout.objects.get()
        gpx_workout = workout.gpx_set.get()

        self.assertEqual(None, gpx_workout.average_hr())
        self.assertEqual(None, gpx_workout.average_cad())

    def test_make_sure_2d_points_are_imported_from_gpx(self):
        self.request.FILES['gpxfile'] = self._make_simple_upload_file("3p_simplest.gpx")

        gpx.upload_gpx(self.request)

        points = models.GpxTrackPoint.objects.all()
        self.assertEqual(3, len(points))

        self.assertEqual((Decimal('51.05772623'), Decimal('16.99809956'), datetime.datetime(2016, 7, 30, 6, 22, 5, tzinfo=pytz.utc)),
                         (points[0].lat, points[0].lon, points[0].time))

        self.assertEqual((Decimal('51.05773386'), Decimal('16.99807215'), datetime.datetime(2016, 7, 30, 6, 22, 6, tzinfo=pytz.utc)),
                         (points[1].lat, points[1].lon, points[1].time))

        self.assertEqual((Decimal('51.05774031'), Decimal('16.99804198'), datetime.datetime(2016, 7, 30, 6, 22, 7, tzinfo=pytz.utc)),
                         (points[2].lat, points[2].lon, points[2].time))

    def test_make_sure_hr_and_cad_data_is_imported_from_gpx(self):
        self.request.FILES['gpxfile'] = self._make_simple_upload_file("3p_hr_cad.gpx")

        gpx.upload_gpx(self.request)

        points = models.GpxTrackPoint.objects.all()

        self.assertEqual(100, points[0].hr)
        self.assertEqual(110, points[1].hr)
        self.assertEqual(120, points[2].hr)

        self.assertEqual(60, points[0].cad)
        self.assertEqual(70, points[1].cad)
        self.assertEqual(80, points[2].cad)

    def test_detect_already_existing_equal_workout(self):
        self.request.FILES['gpxfile'] = self._make_simple_upload_file("3p_simplest.gpx")
        gpx.upload_gpx(self.request)

        with self.assertRaises(gpx.WorkoutAlreadyExists):
            self.request.FILES['gpxfile'] = self._make_simple_upload_file("3p_simplest.gpx")
            gpx.upload_gpx(self.request)
