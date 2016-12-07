import pyproj
from math import sqrt
import json
import datetime
import numpy as np
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


def _unique_rows(data):
    uniq = np.unique(data.view(data.dtype.descr * data.shape[1]))
    return uniq.view(data.dtype).reshape(-1, data.shape[1])


def _process_points(coordinates):
    points = np.array([_web_mercator(p) for p in coordinates])
    points = np.apply_along_axis(hexagons.point_to_hexagon, 1, points)
    return _unique_rows(points).tolist()


ACTIVITIES = [{'activity_type': 'running', 'color': 'blue'},
              {'activity_type': 'cycling', 'color': 'red'},
              {'activity_type': 'walking', 'color': 'green'}]


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
