import pyproj
from math import sqrt
import json
import datetime
import decimal

from django.utils import timezone
from . import models
from .hexagons import point_to_hexagon


EPSG4326 = pyproj.Proj('+init=EPSG:4326')
WEB_MERCATOR = pyproj.Proj('+init=EPSG:3857')


def _web_mercator(point):
    lon, lat = point
    return pyproj.transform(EPSG4326, WEB_MERCATOR, lon, lat)


def _process_points(points):
    return list({point_to_hexagon(_web_mercator(point)) for point in points})


ACTIVITIES = [{'name': 'running', 'color': 'blue'},
              {'name': 'cycling', 'color': 'red'},
              {'name': 'walking', 'color': 'green'}]


def _collect_points(user, name, days=None):
    points = models.GpxTrackPoint.objects.filter(gpx__workout__user=user)

    if days is not None:
        date = timezone.now() - datetime.timedelta(days=days)
        points = points.filter(time__gt=date)

    points = points.filter(gpx__name=name)
    points = points.values_list('lon', 'lat')
    return _process_points(points)


def _make_activity(user, activity, days):
    return {'name': activity['name'],
            'color': activity['color'],
            'points': _collect_points(user, activity['name'], days)}


def generate_heatmap(user, days=None):
    activities = [_make_activity(user, activity, days) for activity in ACTIVITIES]

    return {'json': json.dumps(activities),
            'activities': activities}
