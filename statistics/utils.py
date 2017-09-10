from django.db.models import Sum, Min, Max, F


def sum(source, field_name):
    '''
    Quick sum of @field_name from @source which is a Django QuerySet.
    '''
    value = source.aggregate(value=Sum(field_name))['value']
    return value if value else 0


def max(source, field_name):
    '''
    Quick max of @field_name from @source which is a Django QuerySet.
    '''
    value = source.aggregate(value=Max(field_name))['value']
    return value if value else 0


def between_timerange(source, rng, time_field='started'):
    '''
    Filter QuerySet with time range.
    '''
    if rng is not None and rng.fully_bound():
        kwargs = {'{}__gte'.format(time_field): rng.start,
                  '{}__lt'.format(time_field): rng.end}
        return source.filter(**kwargs)
    else:
        return source


class Metric:
    """Used by activities module as workout metric."""

    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __iter__(self):
        yield self.name
        yield self.value

    def __len__(self):
        return 2
