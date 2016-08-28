import datetime
from django.db import models
from django.db.models import Count
from django.contrib.auth.models import User
from django.template import defaultfilters
from django.db.models import Sum, Avg
from django.utils import timezone

from . import units

class Workout(models.Model):
    user = models.ForeignKey(User)
    started = models.DateTimeField(null=True, default=None)
    finished = models.DateTimeField(null=True, default=None)

    def __str__(self):
        return "{} at {}".format(self.type(), self.started)

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

    def total_reps(self):
        return Reps.objects.filter(excercise__workout=self).aggregate(Sum('reps'))['reps__sum'] or '-'

    def duration(self):
        if self.started is not None and self.finished is not None:
            return self.finished - self.started
        else:
            return datetime.timedelta()

    def volume(self):
        if self.is_gpx():
            return units.km_from_m(self.gpx_set.get().length_2d)
        else:
            return self.total_reps()

    def type(self):
        if self.is_gpx():
            return self.gpx_set.get().activity_type
        else:
            return 'STRENGTH'

    def utd(self):
        """ userfriendly training data string """
        return '\n'.join(map(lambda x: x.utd(), self.excercise_set.all()))


class Excercise(models.Model):
    def utd(self):
        """ userfriendly training data string """
        reps = self.reps_set.all()
        r = ' '.join(map(lambda x: str(x.reps), reps))
        return ': '.join([self.name, r])

    def total_reps(self):
        reps = self.reps_set.all()
        return sum(map(lambda x: x.reps, reps))

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

    @staticmethod
    def most_common():
        return Excercise.objects.values_list('name').annotate(count=Count('name')).order_by('-count')


class Reps(models.Model):
    excercise = models.ForeignKey(Excercise)
    reps = models.IntegerField()

    @staticmethod
    def most_common():
        return Reps.objects.values_list('reps').annotate(rep_count=Count('reps')).order_by('-rep_count')


class Gpx(models.Model):
    workout = models.ForeignKey(Workout)
    activity_type = models.CharField(max_length=20)
    length_2d = models.IntegerField(null=True, default=None)
    length_3d = models.IntegerField(null=True, default=None)

    def polyline_json(self):
        def take_coords(point):
            return float(point.lat), float(point.lon)

        points = map(take_coords, self.gpxtrackpoint_set.all())

        import json
        return json.dumps(list(points))

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
