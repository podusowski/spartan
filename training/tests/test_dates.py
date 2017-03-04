import pytz
import datetime

from django.test import TestCase, RequestFactory

from training import dates
from tests.utils import time


FIRST_JAN_2016 = time(2016, 1, 1, 0, 0, 0)
TENTH_JAN_2016 = time(2016, 1, 10, 0, 0, 0)
LAST_JAN_2016 = time(2016, 1, 31, 23, 59, 59, 999999)

JANUARY_2016 = dates.TimeRange(FIRST_JAN_2016, LAST_JAN_2016)


class UtilsTestCase(TestCase):
    def test_week_range(self):
        weeks = list(dates.week_range(start=time(2016, 8, 7, 0, 0, 0),
                                      end=time(2016, 8, 1, 0, 0, 0)))

        self.assertEqual(1, len(weeks))
        self.assertEqual((time(2016, 8, 1, 0, 0, 0), time(2016, 8, 7, 23, 59, 59)), weeks[0])

        weeks = dates.week_range(start=time(2016, 8, 7, 0, 0, 0),
                                 end=time(2016, 8, 2, 0, 0, 0))

        self.assertEqual(1, len(list(weeks)))

    def test_week_range_by_limit(self):
        weeks = list(dates.week_range(start=time(2016, 8, 7, 0, 0, 0), number=3))
        self.assertEqual(3, len(weeks))

    def test_insufficient_parameters(self):
        with self.assertRaises(AttributeError):
            list(dates.week_range()) # evaluate generator

    def test_month_range(self):
        months = list(dates.month_range(start=time(2016, 2, 1, 0, 0, 0),
                                        end=time(2015, 12, 1, 0, 0, 0)))

        self.assertEqual(3, len(months))
        self.assertEqual((time(2016, 2, 1, 0, 0, 0), time(2016, 2, 29, 23, 59, 59, 999999)), months[0])
        self.assertEqual((time(2016, 1, 1, 0, 0, 0), time(2016, 1, 31, 23, 59, 59, 999999)), months[1])
        self.assertEqual((time(2015, 12, 1, 0, 0, 0), time(2015, 12, 31, 23, 59, 59, 999999)), months[2])

    def test_month_range_by_limit(self):
        months = list(dates.month_range(start=FIRST_JAN_2016, number=3))
        self.assertEqual(3, len(months))

    def test_this_month(self):
        self.assertEqual(JANUARY_2016, dates.this_month(now=TENTH_JAN_2016))

    def test_progress_in_date_range(self):
        self.assertEqual(0, JANUARY_2016.progress(FIRST_JAN_2016))
        self.assertEqual(30, JANUARY_2016.progress(TENTH_JAN_2016))
        self.assertEqual(100, JANUARY_2016.progress(LAST_JAN_2016))
