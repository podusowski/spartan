import pyproj
from math import sqrt
import json
import datetime

from django.utils import timezone
from . import models
from . import hexagons


EPSG4326 = pyproj.Proj('+init=EPSG:4326')
WEB_MERCATOR = pyproj.Proj('+init=EPSG:3857')


def _dump(data):
    def json_encode_decimal(obj):
        if isinstance(obj, decimal.Decimal):
            return str(obj)
        raise TypeError(repr(obj) + " is not JSON serializable")

    return json.dumps(data, default=json_encode_decimal)


def _web_mercator(point):
    lon, lat = point
    return pyproj.transform(EPSG4326, WEB_MERCATOR, lon, lat)


def _process_points(activity):
    points = map(_web_mercator, activity)
    points = map(hexagons.point_to_hexagon, points)
    points = set(points)
    points = list(points)
    return points


def generate_heatmap(user, days=None):
    points = models.GpxTrackPoint.objects.filter(gpx__workout__user=user)

    if days is not None:
        date = timezone.now() - datetime.timedelta(days=days)
        points = points.filter(time__gt=date)

    points = points.values_list('lon', 'lat', 'gpx__activity_type')

    activities = {}
    for lat, lon, activity_type in points:
        if activity_type not in activities:
            activities[activity_type] = []
        activities[activity_type].append((lat, lon))

    activities = [{'activity_type': activity_type,
                   'points': _process_points(points)} for activity_type, points in activities.items()]

    return {'total_points': len(points),
            'json': _dump(activities),
            'activities': activities}
