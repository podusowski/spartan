import datetime
from django.db.models import Sum, Min, Max, F

from training import models
from training import units


def _sum(source, field_name):
    value = source.aggregate(value=Sum(field_name))['value']
    return value if value else 0


def _max(source, field_name):
    value = source.aggregate(value=Max(field_name))['value']
    return value if value else 0


def _sum_duration(source):
    '''
    Django's SQLite backend doesn't support datetime expressions so we
    have to count this in python
    '''
    return sum([workout.finished - workout.started for workout in source], datetime.timedelta())


def workout(user, name):
    source = models.Gpx.objects.filter(workout__user=user, name=name)
    workouts = models.Workout.objects.filter(user=user, gpx__name=name)

    if not source:
        return {}

    total_distance = _sum(source, 'distance')
    max_distance = _max(source, 'distance')
    total_duration = _sum_duration(workouts)

    return [
            ('total workouts', source.count()),
            ('total distance', units.Volume(meters=total_distance)),
            ('total duration', total_duration),
            ('average distance per workout', units.Volume(meters=total_distance/source.count())),
            ('max distance', units.Volume(meters=max_distance)),
           ]
