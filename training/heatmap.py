import pyproj
from math import sqrt
import json
import datetime
import decimal

from django.utils import timezone
from . import models
from . import hexagons


EPSG4326 = pyproj.Proj('+init=EPSG:4326')
WEB_MERCATOR = pyproj.Proj('+init=EPSG:3857')


def _dump(data):
    return json.dumps(data)


def _web_mercator(point):
    lon, lat = point
    return pyproj.transform(EPSG4326, WEB_MERCATOR, lon, lat)


def _process_points(activity):
    points = map(_web_mercator, activity)
    points = map(hexagons.point_to_hexagon, points)
    points = set(points)
    points = list(points)
    return points


ACTIVITIES = [{'activity_type': 'running', 'color': 'blue'},
              {'activity_type': 'running, trail', 'color': 'black'},
              {'activity_type': 'cycling', 'color': 'red'},
              {'activity_type': 'walking', 'color': 'yellow'},
              {'activity_type': 'hiking', 'color': 'brown'}]


def _collect_points(user, activity_type, days=None):
    points = models.GpxTrackPoint.objects.filter(gpx__workout__user=user)

    if days is not None:
        date = timezone.now() - datetime.timedelta(days=days)
        points = points.filter(time__gt=date)

    points = points.filter(gpx__activity_type=activity_type)
    points = points.values_list('lon', 'lat')
    return _process_points(points)


def generate_heatmap(user, days=None):
    activities = []
    for activity in ACTIVITIES:
        activities.append({'activity_type': activity['activity_type'],
                           'color': activity['color'],
                           'points': _collect_points(user, activity['activity_type'], days)})

    return {'json': _dump(activities),
            'activities': activities}
