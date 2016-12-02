import datetime
import os
import logging
import json
import decimal
import pyproj
import math
from math import sqrt

from django.db import transaction
from django.utils import timezone

import gpxpy

from . import models

class WorkoutAlreadyExists(Exception):
    pass

def _workout_already_exists(user, started, finished):
    try:
        models.Workout.objects.get(user=user, started=started, finished=finished)
        logging.debug("workout already exists")
        return True
    except:
        logging.debug("workout not there")
        return False


def upload_gpx(request):
    content = request.FILES['gpxfile'].read().decode('utf-8')
    save_gpx(request.user, content)


def save_gpx(user, content):
    logging.debug("saving gpx")

    parsed = gpxpy.parse(content)

    started, finished = parsed.get_time_bounds()
    if _workout_already_exists(user, started, finished):
        raise WorkoutAlreadyExists()

    workout = models.Workout.objects.create(user=user,
                                            started=started,
                                            finished=finished)

    gpx = models.Gpx.objects.create(workout=workout,
                                    activity_type = parsed.tracks[0].type,
                                    distance = int(parsed.length_2d()))

    for track in parsed.tracks:
        for segment in track.segments:
            for point in segment.points:
                gpx.gpxtrackpoint_set.create(lat=point.latitude,
                                             lon=point.longitude,
                                             hr=point.extensions.get('hr', None),
                                             cad=point.extensions.get('cad', None),
                                             time=point.time)

import endoapi.endomondo

@transaction.atomic
def _import_endomondo_workout(user, endomondo_workout):
    workout = models.Workout.objects.create(user=user,
                                            started=endomondo_workout.start_time,
                                            finished=endomondo_workout.start_time + endomondo_workout.duration)

    models.EndomondoWorkout.objects.create(workout=workout,
                                           endomondo_id=endomondo_workout.id)

    gpx = models.Gpx.objects.create(workout=workout,
                                    activity_type=endomondo_workout.sport,
                                    distance=endomondo_workout.distance)

    for point in endomondo_workout.points:
        gpx.gpxtrackpoint_set.create(lat=point['lat'],
                                     lon=point['lon'],
                                     hr=point.get('hr', None),
                                     cad=point.get('cad', None),
                                     time=point['time'])


def _endomondo_time_bounds(user):
    workouts = models.Workout.objects.filter(user=user,
                                             endomondoworkout__isnull=False)

    try:
        latest_workout = workouts.latest("started")
        earliest_workout = workouts.earliest("started")

        return latest_workout.started, earliest_workout.started

    except Exception as e:
        logging.warn(str(e))
        return None, None


def synchronize_endomondo(user, max_results=None):
    key = models.AuthKeys.objects.get(user=user, name="endomondo")
    endomondo = endoapi.endomondo.Endomondo(token=key.key)

    newest, oldest = _endomondo_time_bounds(user)

    endomondo_workouts = endomondo.fetch(max_results=max_results, before=oldest, after=newest)

    count = 0
    for endomondo_workout in endomondo_workouts:
        if not _workout_already_exists(user,
                                       endomondo_workout.start_time,
                                       endomondo_workout.start_time + endomondo_workout.duration):
            try:
                _import_endomondo_workout(user, endomondo_workout)
                count += 1
            except Exception as e:
                logging.exception('error during workout import')

    logging.debug('imported {} workouts'.format(count))
    return count


def connect_to_endomondo(user, email, password):
    endomondo = endoapi.endomondo.Endomondo(email=email, password=password)
    token = endomondo.token
    models.AuthKeys.objects.update_or_create(defaults={'key': token}, user=user, name="endomondo")


def endomondo_key(user):
    try:
        return models.AuthKeys.objects.get(user=user, name="endomondo")
    except:
        return None


def disconnect_endomondo(user):
    models.AuthKeys.objects.get(user=user, name="endomondo").delete()


def purge_endomondo_workouts(user):
    models.Workout.objects.filter(user=user, endomondoworkout__isnull=False).delete()


EPSG4326 = pyproj.Proj('+init=EPSG:4326')
WEB_MERCATOR = pyproj.Proj('+init=EPSG:3857')

size = 100


def hex_to_pixel(h):
    q, r = h
    x = size * 3/2 * q
    y = size * sqrt(3) * (r + q/2)
    return x, y


def hex_to_pixel(h):
    x = size * sqrt(3) * (q + r/2)
    y = size * 3/2 * r
    return x, y


def hex_to_pixel(h):
    q, r = h
    x = size * 3/2 * q
    y = size * sqrt(3) * (r + q/2)
    return x, y


def cube_to_hex(h): # axial
    x, _, z = h
    q = x
    r = z
    return q, r


def hex_to_cube(h): # axial
    q, r = h
    x = q
    z = r
    y = -x-z
    return (x, y, z)


def cube_round(h):
    x, y, z = h

    rx = round(x)
    ry = round(y)
    rz = round(z)

    x_diff = abs(rx - x)
    y_diff = abs(ry - y)
    z_diff = abs(rz - z)

    if x_diff > y_diff and x_diff > z_diff:
        rx = -ry-rz
    elif y_diff > z_diff:
        ry = -rx-rz
    else:
        rz = -rx-ry

    return rx, ry, rz


def hex_round(h):
    return cube_to_hex(cube_round(hex_to_cube(h)))


def pixel_to_hex(point):
    x, y = point
    q = x * 2/3 / size
    r = (-x / 3 + sqrt(3)/3 * y) / size
    return hex_round((q, r))


def generate_heatmap(user):
    def r(value):
        return int(value / 100) * 100 #round(float(value), 1)

    def loose_precision(gpx_point):
        lon, lat = gpx_point
        return r(lon), r(lat)

    def web(point):
        lon, lat = point
        return pyproj.transform(EPSG4326, WEB_MERCATOR, lon, lat)

    def hexagonal(point):
        h = pixel_to_hex(point)
        return hex_to_pixel(h)

    def json_encode_decimal(obj):
        if isinstance(obj, decimal.Decimal):
            return str(obj)
        raise TypeError(repr(obj) + " is not JSON serializable")

    #time = timezone.now().date() - datetime.timedelta(days=14)
    #points = models.GpxTrackPoint.objects.filter(gpx__workout__user=user, time__gt=time).values_list('lon', 'lat')
    points = models.GpxTrackPoint.objects.filter(gpx__workout__user=user).values_list('lon', 'lat')

    points = map(web, points)
    points = map(loose_precision, points)

    points = map(hexagonal, points)
    points = set(points)

    points = list(points)

    return json.dumps(points, default=json_encode_decimal)
