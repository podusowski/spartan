import datetime
import pytz
from decimal import Decimal

from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser, User

from training import models
from training.models import Workout, Excercise
from training import views


class ViewsTestCase(TestCase):
    def setUp(self):
        self.request_factory = RequestFactory()
        self.user = User.objects.create_user(username='jacob', email='jacob@…', password='top_secret')

    def _start_workout(self):
        request = self.request_factory.get('')
        request.user = self.user

        views.start_workout(request)

        # workout gets started when first excercise starts
        workout = Workout.objects.get()
        self.assertFalse(workout.live())

        return workout

    def _finish_workout(self, workout):
        request = self.request_factory.get('')
        request.user = self.user

        views.finish_workout(request, workout.pk)
        workout.refresh_from_db()
        self.assertFalse(workout.live())
        self.assertIsNotNone(workout.started)
        self.assertIsNotNone(workout.finished)

    def _start_excercise(self, workout):
        request = self.request_factory.post('', {'name': "push-up"})
        request.user = self.user
        views.add_excercise(request, workout.pk)
        excercise = Excercise.objects.latest('pk')
        return excercise

    def _add_reps(self, excercise, reps):
        request = self.request_factory.post('', {'reps': reps})
        request.user = self.user
        views.add_reps(request, excercise.pk)
        excercise.refresh_from_db()

    def test_full_session(self):
        workout = self._start_workout()

        push_ups = self._start_excercise(workout)

        workout.refresh_from_db()
        self.assertTrue(workout.live())

        self._add_reps(push_ups, "10")
        self._add_reps(push_ups, "10")

        self.assertEqual(20, sum(map(lambda x: x.reps, push_ups.reps_set.all())))

        crunches = self._start_excercise(workout)
        self._add_reps(crunches, "20")

        self._finish_workout(workout)


import os
from training import gpx
from django.core.files.uploadedfile import SimpleUploadedFile


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

        workout = Workout.objects.get()
        self.assertTrue(workout.is_gpx());
        self.assertEqual(datetime.datetime(2016, 7, 30, 6, 22, 5, tzinfo=pytz.utc), workout.started)
        self.assertEqual(datetime.datetime(2016, 7, 30, 6, 22, 7, tzinfo=pytz.utc), workout.finished)

        gpx_workout = workout.gpx_set.get()
        self.assertEqual("RUNNING", gpx_workout.activity_type)
        self.assertEqual(4, gpx_workout.length_2d)
        self.assertEqual(10, gpx_workout.length_3d)

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

from training import statistics

def _time(y, month, d, h, m, s):
    return datetime.datetime(y, month, d, h, m, s, tzinfo=pytz.utc)

class UtilsTestCase(TestCase):
    def test_week_range(self):
        weeks = list(statistics.week_range(start=_time(2016, 8, 7, 0, 0, 0),
                                           end=_time(2016, 8, 1, 0, 0, 0)))

        self.assertEqual(1, len(weeks))
        self.assertEqual((datetime.datetime(2016, 8, 1, 0, 0, 0, tzinfo=pytz.utc),
                          datetime.datetime(2016, 8, 7, 23, 59, 59, tzinfo=pytz.utc)),
                         weeks[0])


        weeks = statistics.week_range(start=datetime.datetime(2016, 8, 7, 0, 0, 0, tzinfo=pytz.utc),
                                      end=datetime.datetime(2016, 8, 2, 0, 0, 0, tzinfo=pytz.utc))

        self.assertEqual(1, len(list(weeks)))

    def test_week_range_by_limit(self):
        weeks = list(statistics.week_range(start=_time(2016, 8, 7, 0, 0, 0), number=3))
        self.assertEqual(3, len(weeks))
