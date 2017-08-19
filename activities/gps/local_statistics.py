from django.db.models import Sum, Min, Max

from training import models
from training import units


def _sum(source, field_name):
    value = source.aggregate(value=Sum(field_name))['value']
    return value if value else 0


def _max(source, field_name):
    value = source.aggregate(value=Max(field_name))['value']
    return value if value else 0


def workout(user, name):
    source = models.Gpx.objects.filter(workout__user=user, name=name)

    if not source:
        return {}

    total_distance = _sum(source, 'distance')
    max_distance = _max(source, 'distance')

    return [
            ('total workouts', source.count()),
            ('total distance', units.Volume(meters=total_distance)),
            ('average distance per workout', units.Volume(meters=total_distance/source.count())),
            ('max distance', units.Volume(meters=max_distance)),
           ]
