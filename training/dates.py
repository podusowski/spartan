import arrow
import datetime

from django.utils import timezone


class TimeRange:
    def __init__(self, start, end) -> None:
        self.start = start
        self.end = end

    def __str__(self) -> str:
        return "{} - {}".format(self.start, self.end)

    def __repr__(self) -> str:
        return "TimeRange({}, {})".format(repr(self.start), repr(self.end))

    def __eq__(self, other):
        return (self.start, self.end) == (other.start, other.end)

    def fully_bound(self):
        return None not in [self.start, self.end]

    def progress(self, date) -> int:
        '''
        Return percentage of the date in the context of given TimeRange.
        For example, if TimeRange is a month and middle day is given, it will
        return 50.
        '''
        s = self.start.toordinal()
        e = self.end.toordinal()
        d = date.toordinal()

        return round((d - s) / (e - s) * 100)

    URL_SEP = '^'
    FORMAT = '%Y-%m-%d %H:%M:%S.%f %z'

    def tourl(self) -> str:
        '''
        Convert range to string suitable for URL parameters.
        '''
        parts = tuple(d.strftime(TimeRange.FORMAT) for d in (self.start, self.end))
        return TimeRange.URL_SEP.join(parts)

    @classmethod
    def fromurl(cls, ordinal):
        '''
        Construct TimeRange from URL parameter.
        '''
        parts = tuple(datetime.datetime.strptime(s, TimeRange.FORMAT) for s in ordinal.split(TimeRange.URL_SEP))
        return cls(*parts)


def week_range(number=None, end=None, start=timezone.now()):
    if number is None and end is None:
        raise AttributeError("number or end parameter must be provided")

    week_start = arrow.get(start).floor('week').datetime
    week = datetime.timedelta(weeks=1)
    second = datetime.timedelta(seconds=1)

    while True:
        yield (week_start, week_start + week - second)
        week_start -= week

        if end is not None and week_start < end:
            break

        if number is not None:
            number -= 1
            if number <= 0:
                break


def month_range(number=None, end=None, start=timezone.now()):
    week_start = arrow.get(start).floor('month').datetime

    while True:
        yield (week_start, arrow.get(week_start).ceil('month').datetime)
        week_start = arrow.get(week_start).replace(months=-1).datetime

        if end is not None and week_start < end:
            break

        if number is not None:
            number -= 1
            if number <= 0:
                break


def this_month(now=timezone.now()):
    months = list(month_range(1, start=now))
    return TimeRange(*months[0])


def days_left_in_this_month(now=timezone.now()):
    month = this_month(now=now)
    return month.end.toordinal() - now.toordinal()
