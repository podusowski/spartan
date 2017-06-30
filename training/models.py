import datetime
import json
import logging

from django.db import models
from django.db.models import Count
from django.contrib.auth.models import User
from django.template import defaultfilters
from django.db.models import Sum, Avg
from django.utils import timezone

from . import units
import activities.registry

class Workout(models.Model):
    user = models.ForeignKey(User)
    activity_type = models.CharField(max_length=200, default=None)

    @property
    def workout_type(self):
        from_gpx = list(map(lambda x: x.name.lower(), self.gpx_set.all()))
        return from_gpx[0] if len(from_gpx) > 0 else 'strength'

    started = models.DateTimeField(null=True, default=None)
    finished = models.DateTimeField(null=True, default=None)

    def __str__(self):
        return "{}.{} at {} by {}".format(self.activity_type, self.workout_type, self.started, self.user)

    def live(self):
        return self.started is not None and self.finished is None

    def start(self):
        if self.live():
            raise RuntimeError("session is already started")

        if self.finished is not None:
            raise RuntimeError("tried to start already finished session")

        self.started = timezone.now()

    def finish(self):
        if self.started is None:
            raise RuntimeError("tried to finish not started session")

        if self.finished is not None:
            raise RuntimeError("tried to finish already finished session")

        self.finished = timezone.now()

    def duration(self):
        if self.started is not None and self.finished is not None:
            return self.finished - self.started
        else:
            return datetime.timedelta()

    @property
    def volume(self):
        return activities.registry.import_module(self).volume(self)

    class Meta:
        ordering = ['-started']


class Excercise(models.Model):
    @property
    def volume(self):
        reps = self.reps_set.aggregate(Sum('reps'))['reps__sum']
        duration = self.timers_set.aggregate(value=Sum('duration'))['value']

        if reps:
            return units.Volume(reps=reps)
        else:
            return units.Volume(seconds=duration.total_seconds())

    def duration(self):
        if self.time_started is not None and self.time_finished is not None:
            return self.time_finished - self.time_started
        else:
            return datetime.timedelta()

    workout = models.ForeignKey(Workout)
    name = models.CharField(max_length=200)
    time_started = models.DateTimeField(null=True, default=None)
    time_finished = models.DateTimeField(null=True, default=None)
    time_updated = models.DateTimeField(null=True, default=None)

    class Meta:
        ordering = ['-time_started']


class Reps(models.Model):
    excercise = models.ForeignKey(Excercise)
    reps = models.IntegerField()

    class Meta:
        ordering = ['pk']


class Timers(models.Model):
    '''
    Timer based excercises tracks time instead of reps. Example
    of such workout is plank.
    '''
    excercise = models.ForeignKey(Excercise)
    time_started = models.DateTimeField(null=True, default=None)
    duration = models.DurationField(null=True, default=None)

    class Meta:
        ordering = ['pk']


class SportField(models.CharField):
    def __init__(self, *args, **kwargs):
        super(SportField, self).__init__(*args, **kwargs)

    def get_prep_value(self, value):
        v = super(SportField, self).get_prep_value(value)
        return v.lower() if v else None


class Gpx(models.Model):
    workout = models.ForeignKey(Workout)
    name = SportField(max_length=20)
    distance = models.IntegerField(null=True, default=None)

    def points_as_json(self):
        def make_point(point):
            return {'lat': float(point.lat),
                    'lon': float(point.lon),
                    'hr': point.hr,
                    'cad': point.cad,
                    'time': point.time.isoformat()}

        points = map(make_point, self.gpxtrackpoint_set.all().order_by('time'))

        return json.dumps(list(points))

    def _average(self, name):
        avg = self.gpxtrackpoint_set.aggregate(value=Avg(name))['value']
        return None if avg is None else round(avg)

    def average_hr(self):
        return self._average('hr')

    def average_cad(self):
        return self._average('cad')

    def speed_or_pace(self):
        m_per_s = 0
        try:
            m_per_s = self.distance / self.workout.duration().total_seconds()
        except:
            pass

        return units.mpkm_from_mps(m_per_s)


class GpxTrackPoint(models.Model):
    gpx = models.ForeignKey(Gpx)
    lat = models.DecimalField(max_digits=10, decimal_places=8)
    lon = models.DecimalField(max_digits=11, decimal_places=8)
    hr = models.PositiveSmallIntegerField(null=True, default=None)
    cad = models.PositiveSmallIntegerField(null=True, default=None)
    time = models.DateTimeField()


class AuthKeys(models.Model):
    user = models.ForeignKey(User)
    name = models.CharField(max_length=200)
    key = models.CharField(max_length=200)


class EndomondoWorkout(models.Model):
    endomondo_id = models.IntegerField()
    workout = models.ForeignKey(Workout)


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    timezone = models.CharField(max_length=30, null=True, default=None)
