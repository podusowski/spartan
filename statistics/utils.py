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
