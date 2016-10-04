import arrow
import datetime

from django.utils import timezone

def week_range(number:int=None, end=None, start=timezone.now()):
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
