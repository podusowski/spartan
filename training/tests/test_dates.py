import pytz
import datetime
import pytest

from training import dates
from tests.utils import time


FIRST_JAN_2016 = time(2016, 1, 1, 0, 0, 0)
TENTH_JAN_2016 = time(2016, 1, 10, 0, 0, 0)
LAST_JAN_2016 = time(2016, 1, 31, 23, 59, 59, 999999)

JANUARY_2016 = dates.TimeRange(FIRST_JAN_2016, LAST_JAN_2016)


def test_week_range():
    weeks = list(dates.week_range(start=time(2016, 8, 7, 0, 0, 0),
                                    end=time(2016, 8, 1, 0, 0, 0)))

    assert 1 == len(weeks)
    assert (time(2016, 8, 1, 0, 0, 0), time(2016, 8, 7, 23, 59, 59)) == weeks[0]

    weeks = dates.week_range(start=time(2016, 8, 7, 0, 0, 0),
                               end=time(2016, 8, 2, 0, 0, 0))

    assert 1 == len(list(weeks))


def test_week_range_by_limit():
    weeks = list(dates.week_range(start=time(2016, 8, 7, 0, 0, 0), number=3))
    assert 3 == len(weeks)


def test_insufficient_parameters():
    with pytest.raises(AttributeError):
        list(dates.week_range()) # evaluate generator


def test_month_range():
    months = list(dates.month_range(start=time(2016, 2, 1, 0, 0, 0),
                                    end=time(2015, 12, 1, 0, 0, 0)))

    assert 3 == len(months)
    assert (time(2016, 2, 1, 0, 0, 0), time(2016, 2, 29, 23, 59, 59, 999999)) == months[0]
    assert (time(2016, 1, 1, 0, 0, 0), time(2016, 1, 31, 23, 59, 59, 999999)) == months[1]
    assert (time(2015, 12, 1, 0, 0, 0), time(2015, 12, 31, 23, 59, 59, 999999)) == months[2]


def test_month_range_by_limit():
    months = list(dates.month_range(start=FIRST_JAN_2016, number=3))
    assert 3 == len(months)


def test_this_month():
    assert JANUARY_2016 == dates.this_month(now=TENTH_JAN_2016)


def test_progress_in_date_range():
    assert 0 == JANUARY_2016.progress(FIRST_JAN_2016)
    assert 30 == JANUARY_2016.progress(TENTH_JAN_2016)
    assert 100 == JANUARY_2016.progress(LAST_JAN_2016)


def test_days_left_in_month():
    assert 30 == dates.days_left_in_this_month(now=JANUARY_2016.start)
