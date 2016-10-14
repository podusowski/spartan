import os
import pytz
import datetime


GPX_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gpx')


def time(y, month, d, h=0, m=0, s=0, ms=0):
    return datetime.datetime(y, month, d, h, m, s, ms, tzinfo=pytz.utc)
