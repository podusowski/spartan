import logging
import datetime
from django.db.models import Sum, Min, Max

from training import models
from training import units
from statistics import utils
from statistics.utils import Metric
from training import dates


def _sum_duration(source):
    """Django's SQLite backend doesn't support datetime expressions so we
       have to count this in python"""
    return sum([workout.duration for workout in source], datetime.timedelta())


def first_time(user, name):
    source = models.Excercise.objects.filter(workout__user=user, name=name)
    return source.aggregate(earliest=Min('workout__started'))["earliest"]


def workout(user, name, rng=None):
    source = models.Excercise.objects.filter(workout__user=user, name=name)
    source = utils.between_timerange(source, rng, time_field="workout__started")

    if not source:
        logging.debug("no '%s' between '%s'", name, rng)
        return {}

    reps = utils.sum(source, 'reps__reps')
    max_reps_per_series = utils.max(source, 'reps__reps')

    max_reps_per_workout = (source.annotate(total_reps=Sum('reps__reps'))
                                  .order_by('-total_reps')
                                  .first()
                                  .total_reps)

    def round_timedelta(t):
        return t - datetime.timedelta(microseconds=t.microseconds)

    total_duration = round_timedelta(_sum_duration(source))

    series = models.Reps.objects.filter(excercise__workout__user=user,
                                        excercise__name=name)

    series = utils.between_timerange(series, rng, time_field="excercise__workout__started").count()

    return [
            Metric('total workouts', source.count()),
            Metric('total duration', total_duration),
            Metric('total series', series),
            Metric('total reps', units.Volume(reps=reps)),
            Metric('average reps per workout', round(reps / source.count())),
            Metric('average reps per series', round(reps / series)),
            Metric('max reps per series', max_reps_per_series),
            Metric('max reps per workout', max_reps_per_workout),
           ]


def metric_chart(user, excercise_name: str, metric_name: str):
    start = first_time(user, excercise_name)

    if start is None:
        logging.warn("It seems that there is no such excercise")
        return

    for month in dates.month_range(end=start):
        metrics = dict(workout(user, excercise_name, month))
        logging.debug("Workout stats for range %s: %s", month, metrics)

        value = 0
        if metric_name in metrics:
            value = metrics[metric_name]

        yield month, value
