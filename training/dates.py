import arrow
import datetime

from django.utils import timezone


class TimeRange:
    def __init__(self, start, end) -> None:
        self.start = start
        self.end = end

    def __str__(self) -> str:
        return "{} - {}".format(self.start, self.end)

    def __eq__(self, other):
        return (self.start, self.end) == (other.start, other.end)

    def fully_bound(self):
        return None not in [self.start, self.end]

    def progress(self, date):
        s = self.start.toordinal()
        e = self.end.toordinal()
        d = date.toordinal()

        return round((d - s) / (e - s) * 100)


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
