from django import template

register = template.Library()

@register.filter
def duration(value):
    return 'took' + str(value)
