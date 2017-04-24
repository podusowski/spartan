import datetime
import os
import logging
import json
import decimal
import math
from math import sqrt

from django.utils import timezone

import gpxpy

from training import models
from . import gps_workout


class WorkoutAlreadyExists(Exception):
    pass


def upload_gpx(request):
    content = request.FILES['gpxfile'].read().decode('utf-8')
    save_gpx(request.user, content)


def save_gpx(user, content):
    logging.debug("saving gpx")

    parsed = gpxpy.parse(content)

    started, finished = parsed.get_time_bounds()
    if gps_workout.exists(user, started, finished):
        raise WorkoutAlreadyExists()

    workout = models.Workout.objects.create(user=user,
                                            started=started,
                                            finished=finished)

    gpx = models.Gpx.objects.create(workout=workout,
                                    name=parsed.tracks[0].type,
                                    distance=int(parsed.length_2d()))

    for track in parsed.tracks:
        for segment in track.segments:
            for point in segment.points:
                gpx.gpxtrackpoint_set.create(lat=point.latitude,
                                             lon=point.longitude,
                                             hr=point.extensions.get('hr', None),
                                             cad=point.extensions.get('cad', None),
                                             time=point.time)


def workout_types(user):
    return set(models.Gpx.objects.filter(workout__user=user).values_list('name', flat=True))
