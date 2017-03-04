import logging
import pytz

from django import forms
from django.utils import timezone as django_tz
from django.utils.deprecation import MiddlewareMixin

from training import models


class TimezoneMiddleware(MiddlewareMixin):
    def process_request(self, request):
        django_tz.activate(timezone(request.user))


TIMEZONES = zip(pytz.all_timezones, pytz.all_timezones)


class UserProfileForm(forms.Form):
    timezone = forms.ChoiceField(label='time zone', choices=TIMEZONES)


def timezone(user):
    try:
        tz = pytz.timezone(models.UserProfile.objects.get(user=user).timezone)
    except Exception as e:
        logging.debug(str(e))
        tz = pytz.utc

    return tz


def save_timezone(user, value):
    try:
        tz = pytz.timezone(value)
    except pytz.exceptions.UnknownTimeZoneError as e:
        tz = pytz.utc

    models.UserProfile.objects.update_or_create(defaults={'timezone': tz.zone}, user=user)
