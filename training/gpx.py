import datetime
import os

from . import gpxpy
from . import models

def save_gpx(request):
    workout = models.Workout(user=request.user)
    workout.save()
    gpx = models.Gpx(workout=workout, gpx=request.FILES['gpxfile'])

    parsed = gpxpy.parse(gpx.gpx.read().decode('utf-8'))

    workout.started, workout.finished = parsed.get_time_bounds()
    workout.save()

    gpx.activity_type = parsed.tracks[0].type
    gpx.length_2d = int(parsed.length_2d())
    gpx.length_3d = int(parsed.length_3d())

    gpx.save()

    for track in parsed.tracks:
        for segment in track.segments:
            for point in segment.points:
                gpx.gpxtrackpoint_set.create(lat=point.latitude,
                                             log=point.longitude,
                                             time=point.time)
