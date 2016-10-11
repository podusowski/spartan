import logging
import pytz

from django import forms

from training import models


class UserProfileForm(forms.Form):
    timezone = forms.CharField(label='time zone')


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
