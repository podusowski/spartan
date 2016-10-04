import pytz
import datetime

from django.test import TestCase, RequestFactory

from training import dates


def _time(y, month, d, h, m, s):
    return datetime.datetime(y, month, d, h, m, s, tzinfo=pytz.utc)


class UtilsTestCase(TestCase):
    def test_week_range(self):
        weeks = list(dates.week_range(start=_time(2016, 8, 7, 0, 0, 0),
                                      end=_time(2016, 8, 1, 0, 0, 0)))

        self.assertEqual(1, len(weeks))
        self.assertEqual((datetime.datetime(2016, 8, 1, 0, 0, 0, tzinfo=pytz.utc),
                          datetime.datetime(2016, 8, 7, 23, 59, 59, tzinfo=pytz.utc)),
                         weeks[0])


        weeks = dates.week_range(start=datetime.datetime(2016, 8, 7, 0, 0, 0, tzinfo=pytz.utc),
                                      end=datetime.datetime(2016, 8, 2, 0, 0, 0, tzinfo=pytz.utc))

        self.assertEqual(1, len(list(weeks)))

    def test_week_range_by_limit(self):
        weeks = list(dates.week_range(start=_time(2016, 8, 7, 0, 0, 0), number=3))
        self.assertEqual(3, len(weeks))
