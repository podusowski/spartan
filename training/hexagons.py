from math import sqrt


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


def point_to_hexagon(point):
    return hex_to_pixel(pixel_to_hex(point))
