from math import sqrt, floor


_SQRT_3 = sqrt(3)
_SQRT_3_DIV_3 = _SQRT_3 / 3

S = 100
W = S * 2
H = _SQRT_3 / 2 * W

_S_MUL_3 = S * 3
_S_MUL_SQRT_3 = S * _SQRT_3
_TWO_DIV_S = 2/S


def point_to_hexagon(point):
    x, y = point

    x = x / 3
    z = (-x + _SQRT_3_DIV_3 * y) / S
    x = x * _TWO_DIV_S
    y = -x-z

    rx = round(x)
    ry = round(y)
    rz = round(z)

    xd = abs(rx - x)
    yd = abs(ry - y)
    zd = abs(rz - z)

    if xd > yd and xd > zd:
        rx = -ry-rz
    elif yd > zd:
        pass
    else:
        rz = -rx-ry

    rx = rx / 2
    y = _S_MUL_SQRT_3 * (rz + rx)
    x = _S_MUL_3 * rx

    return x, y


def points_to_hexagon(points):
    return [point_to_hexagon(p) for p in points]
