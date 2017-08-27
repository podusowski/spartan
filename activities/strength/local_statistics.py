import datetime
from django.db.models import Sum, Min, Max

from training import models
from training import units
from statistics import utils


def _sum_duration(source):
    '''
    Django's SQLite backend doesn't support datetime expressions so we
    have to count this in python
    '''
    return sum([workout.duration for workout in source], datetime.timedelta())


def workout(user, name):
    source = models.Excercise.objects.filter(workout__user=user, name=name)

    if not source:
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
                                        excercise__name=name).count()

    return [
            ('total workouts', source.count()),
            ('total duration', total_duration),
            ('total series', series),
            ('total reps', units.Volume(reps=reps)),
            ('average reps per workout', round(reps / source.count())),
            ('average reps per series', round(reps / series)),
            ('max reps per series', max_reps_per_series),
            ('max reps per workout', max_reps_per_workout),
           ]
