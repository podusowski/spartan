import collections
import enum
from typing import List

from django.contrib.auth.models import User
from django.utils import timezone

from training import units
from training import dates
from statistics import models
from statistics.statistics import Statistics


Forecast = enum.Enum('Forecast', ['AHEAD', 'ON_TRACK', 'BEHIND', 'DONE'])
Goal = collections.namedtuple('Goal', ['name', 'volume', 'progress', 'percent', 'left', 'forecast'])


class Goals:
    def __init__(self, user: User) -> None:
        self.user = user
        self.statistics = Statistics(user)

    def set(self, name: str, volume: int) -> None:
        models.Goal.objects.update_or_create(user=self.user, name=name, defaults={'volume': volume})

    def delete(self, name: str) -> None:
        models.Goal.objects.filter(user=self.user, name=name).delete()

    def get(self, name) -> Goal:
        for goal in self.all():
            if goal.name == name:
                return goal
        return None

    def _has_goal(self, name: str) -> bool:
        return True if self.get(name) else False

    def workouts_not_having_goal(self):
        workouts = self.statistics.most_popular_workouts()
        return [workout.name for workout in workouts if not self._has_goal(workout.name)]

    def all(self, now=timezone.now()) -> List[Goal]:
        volumes = {f.name: f.volume for f in self.statistics.favourites_this_month()}

        def calculate_forecast(percent):
            date_progress = dates.this_month(now=now).progress(now)

            if percent >= 100:
                return Forecast.DONE

            if percent > date_progress + 10:
                return Forecast.AHEAD

            if percent < date_progress - 10:
                return Forecast.BEHIND

            return Forecast.ON_TRACK

        def make_goal(goal):
            current = volumes.get(goal.name, units.Volume(0))
            percent = round(current.number() / goal.volume * 100)

            return Goal(name=goal.name,
                        volume=goal.volume,
                        progress=current,
                        percent=percent,
                        forecast=calculate_forecast(percent),
                        left=current.left_to(goal.volume))

        return [make_goal(g) for g in models.Goal.objects.filter(user=self.user)]
