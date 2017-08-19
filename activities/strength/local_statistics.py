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
    source = models.Excercise.objects.filter(workout__user=user, name=name)

    if not source:
        return {}

    reps = _sum(source, 'reps__reps')
    max_reps_per_series = _max(source, 'reps__reps')

    series = models.Reps.objects.filter(excercise__workout__user=user,
                                        excercise__name=name).count()

    return [('total workouts', source.count()),
            ('total series', series),
            ('total reps', units.Volume(reps=reps)),
            ('average reps per workout', round(reps / source.count())),
            ('average reps per series', round(reps / series)),
            ('max reps per series', max_reps_per_series)]
