import datetime
from django.db import models
from django.db.models import Count
from django.contrib.auth.models import User
from django.template import defaultfilters
from django.db.models import Sum

class Workout(models.Model):
    user = models.ForeignKey(User)
    started = models.DateTimeField(null=True, default=None)
    finished = models.DateTimeField(null=True, default=None)

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

        self.started = datetime.datetime.now()

    def finish(self):
        if self.started is None:
            raise RuntimeError("tried to finish not started session")

        if self.finished is not None:
            raise RuntimeError("tried to finish already finished session")

        self.finished = datetime.datetime.now()

    def total_reps(self):
        return Reps.objects.filter(excercise__workout=self).aggregate(Sum('reps'))['reps__sum'] or '-'

    def duration(self):
        if self.started is not None and self.finished is not None:
            return self.finished - self.started
        else:
            return datetime.timedelta()

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
    gpx = models.FileField(upload_to='gpx')
