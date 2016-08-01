import datetime
import os

from . import gpxpy
from . import models

def parse(xml):
    gpx = gpxpy.parse(xml)
    track = gpx.tracks[0]
    segment = gpx.tracks[0].segments[0]

    moving_time, stopped_time, moving_distance, stopped_distance, max_speed = segment.get_moving_data()
    start_time, end_time = segment.get_time_bounds()

    return {'moving_time': datetime.timedelta(seconds=moving_time),
            'length_2d': int(segment.length_2d()),
            'length_3d': int(segment.length_3d()),
            'start_time': start_time,
            'end_time': end_time,
            'duration': end_time - start_time,
            'type': track.type,
            'gpxurl': ''}

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
