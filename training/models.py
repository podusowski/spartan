import datetime
from django.db import models
from django.db.models import Count


class Workout(models.Model):
    started = models.DateTimeField(null=True, default=None)
    finished = models.DateTimeField(null=True, default=None)

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
        return sum(map(lambda x: x.total_reps(), self.excercise_set.all()))

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

    workout = models.ForeignKey(Workout)
    name = models.CharField(max_length=200)


class Reps(models.Model):
    excercise = models.ForeignKey(Excercise)
    reps = models.IntegerField()

    @staticmethod
    def most_common():
        return Reps.objects.values_list('reps').annotate(rep_count=Count('reps')).order_by('-rep_count')
