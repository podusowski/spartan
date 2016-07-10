import datetime
from django.db import models


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

    def utd(self):
        """ userfriendly training data string """
        return '\n'.join(map(lambda x: x.utd(), self.excercise_set.all()))


class Excercise(models.Model):
    def utd(self):
        """ userfriendly training data string """
        reps = self.reps_set.all()
        r = ' '.join(map(lambda x: str(x.reps), reps))
        return ': '.join([self.name, r])

    workout = models.ForeignKey(Workout)
    name = models.CharField(max_length=200)


class Reps(models.Model):
    excercise = models.ForeignKey(Excercise)
    reps = models.IntegerField()
