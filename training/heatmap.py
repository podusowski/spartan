import pyproj
from math import sqrt
import json
import datetime

from django.utils import timezone
from . import models


EPSG4326 = pyproj.Proj('+init=EPSG:4326')
WEB_MERCATOR = pyproj.Proj('+init=EPSG:3857')

HEXAGONAL_SIZE = 100


def hex_to_pixel(h):
    q, r = h
    x = HEXAGONAL_SIZE * 3/2 * q
    y = HEXAGONAL_SIZE * sqrt(3) * (r + q/2)
    return x, y


def hex_to_pixel(h):
    x = HEXAGONAL_SIZE * sqrt(3) * (q + r/2)
    y = HEXAGONAL_SIZE * 3/2 * r
    return x, y


def hex_to_pixel(h):
    q, r = h
    x = HEXAGONAL_SIZE * 3/2 * q
    y = HEXAGONAL_SIZE * sqrt(3) * (r + q/2)
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
    q = x * 2/3 / HEXAGONAL_SIZE
    r = (-x / 3 + sqrt(3)/3 * y) / HEXAGONAL_SIZE
    return hex_round((q, r))


def generate_heatmap(user, days=None):
    def web_mercator(point):
        lon, lat = point
        return pyproj.transform(EPSG4326, WEB_MERCATOR, lon, lat)

    def hexagonal(point):
        h = pixel_to_hex(point)
        return hex_to_pixel(h)

    def json_encode_decimal(obj):
        if isinstance(obj, decimal.Decimal):
            return str(obj)
        raise TypeError(repr(obj) + " is not JSON serializable")

    points = models.GpxTrackPoint.objects.filter(gpx__workout__user=user)

    if days is not None:
        date = timezone.now() - datetime.timedelta(days=days)
        points = points.filter(time__gt=date)

    points = points.values_list('lon', 'lat')

    points = map(web_mercator, points)
    points = map(hexagonal, points)
    points = set(points)
    points = list(points)

    return len(points), json.dumps(points, default=json_encode_decimal)
