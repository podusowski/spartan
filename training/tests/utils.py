import pytz
import datetime


def time(y, month, d, h=0, m=0, s=0, ms=0):
    return datetime.datetime(y, month, d, h, m, s, ms, tzinfo=pytz.utc)
