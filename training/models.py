import datetime
import json

from django.db import models
from django.db.models import Count
from django.contrib.auth.models import User
from django.template import defaultfilters
from django.db.models import Sum, Avg
from django.utils import timezone
from django.contrib.gis.geos import GEOSGeometry, Point

from . import units

class Workout(models.Model):
    user = models.ForeignKey(User)
    workout_type = models.CharField(max_length=20, null=False, default="strength")
    started = models.DateTimeField(null=True, default=None)
    finished = models.DateTimeField(null=True, default=None)

    def __str__(self):
        return "{} at {}".format(self.workout_type, self.started)

    def is_gpx(self):
        return len(self.gpx_set.all()) > 0

    def status(self):
        if self.live():
            return 'live'
        elif self.finished is not None:
            return 'finished'
        else:
            return 'not started'

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

    def _total_reps(self):
        return Reps.objects.filter(excercise__workout=self).aggregate(Sum('reps'))['reps__sum'] or 0

    def duration(self):
        if self.started is not None and self.finished is not None:
            return self.finished - self.started
        else:
            return datetime.timedelta()

    def _total_distance(self):
        ''' for gpx workouts '''
        return self.gpx_set.get().length_2d

    def volume(self):
        if self.is_gpx():
            return units.Volume(meters=self._total_distance())
        else:
            return units.Volume(reps=self._total_reps())


class Excercise(models.Model):
    def total_reps(self):
        return self.reps_set.aggregate(Sum('reps'))['reps__sum'] or 0

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
        ordering = ['time_started']


class Reps(models.Model):
    excercise = models.ForeignKey(Excercise)
    reps = models.IntegerField()

    @staticmethod
    def most_common():
        return Reps.objects \
                   .values_list('reps') \
                   .annotate(rep_count=Count('reps')) \
                   .order_by('-reps') \
                   .values_list('reps', flat=True)

    class Meta:
        ordering = ['pk']


class Gpx(models.Model):
    workout = models.ForeignKey(Workout)
    activity_type = models.CharField(max_length=20)
    length_2d = models.IntegerField(null=True, default=None)

    def polyline(self):
        def take_coords(point):
            return float(point.lat), float(point.lon)

        points = map(take_coords, self.gpxtrackpoint_set.all().order_by('time'))

        return json.dumps(list(points))

    def hr_chart(self):
        starting_time = self.gpxtrackpoint_set.first().time
        def take_hr_in_time(point):
            return {'time': float(round(((point.time - starting_time).total_seconds()/60.0),2)),
                    'value': point.hr}

        return list(map(take_hr_in_time, self.gpxtrackpoint_set.all().order_by('time')))

    def cad_chart(self):
        starting_time = self.gpxtrackpoint_set.first().time
        def take_cad_in_time(point):
            return {'time': float(round(((point.time - starting_time).total_seconds()/60.0),2)),
                    'value': point.cad * 2}

        return list(map(take_cad_in_time, self.gpxtrackpoint_set.all().order_by('time')))
 

    def average_hr(self):
        avg_hr = self.gpxtrackpoint_set.aggregate(Avg('hr'))['hr__avg']
        if avg_hr:
            return round(avg_hr)
        else:
            return None 

    def speed_or_pace(self):
        m_per_s = 0
        try:
            m_per_s = self.length_2d / self.workout.duration().total_seconds()
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
