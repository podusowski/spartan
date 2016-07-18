import math

from django import template

register = template.Library()

@register.filter
def duration(value):
    seconds = math.floor(value.total_seconds())

    day = math.floor(seconds / (24 * 60 * 60))
    seconds = seconds % (24 * 60 * 60)

    hour = math.floor(seconds / (60 * 60))
    seconds = seconds % (60 * 60)

    minute = math.floor(seconds / (60))
    seconds = seconds % (60);

    mins_and_secs = str(minute).zfill(2) + 'm:' + str(seconds).zfill(2) + 's'

    if day > 0:
        return '{}d:{}h:{}'.format(day, hour, mins_and_secs)
    elif hour > 0:
        return '{}h:{}'.format(hour, mins_and_secs)
    else:
        return mins_and_secs
