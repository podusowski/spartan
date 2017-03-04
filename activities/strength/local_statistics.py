from django.db.models import Sum, Min, Max

from training import models
from training import units


def _sum(source, field_name):
    value = source.aggregate(value=Sum(field_name))['value']
    return value if value else 0


def workout(user, name):
    source = models.Excercise.objects.filter(workout__user=user, name=name)

    if not source:
        return {}

    reps = _sum(source, 'reps__reps')

    series = models.Reps.objects.filter(excercise__workout__user=user,
                                        excercise__name=name).count()

    return {'total workouts': source.count(),
            'total reps': units.Volume(reps=reps),
            'total series': series,
            'average reps per series': round(reps / series),
            'average reps per workout': round(reps / source.count())}
