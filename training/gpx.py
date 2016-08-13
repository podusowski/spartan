import datetime
import os
import logging

from . import gpxpy
from . import models

class WorkoutAlreadyExists(Exception):
    pass

def _workout_already_exists(request, parsed):
    started, finished = parsed.get_time_bounds()

    try:
        models.Workout.objects.get(user=request.user, started=started, finished=finished)
        logging.debug("workout already exists")
        return True
    except:
        logging.debug("workout not there")
        return False

def save_gpx(request):
    logging.debug("saving gpx")

    parsed = gpxpy.parse(request.FILES['gpxfile'].read().decode('utf-8'))

    if _workout_already_exists(request, parsed):
        raise WorkoutAlreadyExists()

    started, finished = parsed.get_time_bounds()

    workout = models.Workout.objects.create(user=request.user,
                                            started=started,
                                            finished=finished)

    gpx = models.Gpx.objects.create(workout=workout,
                                    activity_type = parsed.tracks[0].type,
                                    length_2d = int(parsed.length_2d()),
                                    length_3d = int(parsed.length_3d()))

    for track in parsed.tracks:
        for segment in track.segments:
            for point in segment.points:
                gpx.gpxtrackpoint_set.create(lat=point.latitude,
                                             lon=point.longitude,
                                             hr=point.extensions.get('hr', None),
                                             cad=point.extensions.get('cad', None),
                                             time=point.time)
