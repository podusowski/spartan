import datetime
from django.db.models import Sum, Min, Max, F

from training import models
from training import units
from statistics import utils
from statistics.utils import Metric


def _sum_duration(source):
    '''
    Django's SQLite backend doesn't support datetime expressions so we
    have to count this in python
    '''
    return sum([workout.finished - workout.started for workout in source], datetime.timedelta())


def workout(user, name, rng=None):
    source = models.Gpx.objects.filter(workout__user=user, name=name)
    source = utils.between_timerange(source, rng, time_field="workout__started")

    workouts = models.Workout.objects.filter(user=user, gpx__name=name)
    workouts = utils.between_timerange(workouts, rng, time_field="started")

    if not source:
        return {}

    total_distance = utils.sum(source, 'distance')
    max_distance = utils.max(source, 'distance')
    total_duration = _sum_duration(workouts)

    return [
            Metric('total workouts', source.count()),
            Metric('total distance', units.Volume(meters=total_distance)),
            Metric('total duration', total_duration),
            Metric('average distance per workout', units.Volume(meters=total_distance/source.count())),
            Metric('max distance', units.Volume(meters=max_distance)),
           ]


def metric_chart(user, excercise_name: str, metric_name: str):
    return []
