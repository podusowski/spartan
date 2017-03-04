import unittest
from django.test import TestCase

from training.hexagons import point_to_hexagon, points_to_hexagon, S, W, H

'''
 lat
  ^
  |
  |      __
  |   __/01\__
  |  /  \__/10\
  |  \__/00\__/
  |  /  \__/  \
  |  \__/  \__/
  |     \__/
  `----------------> lon

00's center is 0,0 in pixels

hexagons.point_to_hexagon((lon, lat))
'''

HALF_H = H / 2
HALF_W = W / 2

# lon diff between 00 and 01
OF = 3/4 * W


class HexagonsTestSuite(TestCase):
    def setUp(self):
        print("size: {}, width: {}, height: {}".format(S, W, H))

    def _expect_point_on_hex(self, h, p):
        self.assertEqual(h, point_to_hexagon(p))

    def test_convert_from_pixel_00(self):
        self._expect_point_on_hex((0, 0), (0, 0))

        self._expect_point_on_hex((0, 0), (0, HALF_H - 1))
        self._expect_point_on_hex((0, 0), (HALF_W - 1, 0))

        self._expect_point_on_hex((0, 0), (0, -HALF_H + 1))
        self._expect_point_on_hex((0, 0), (-HALF_W + 1, 0))

    def test_convert_from_pixel_01(self):
        self._expect_point_on_hex((0, H), (0, HALF_H + 1))
        self._expect_point_on_hex((0, H), (0, H + HALF_H - 1))

    def test_convert_from_pixel_10(self):
        self._expect_point_on_hex((OF, HALF_H), (OF, HALF_H))
        self._expect_point_on_hex((OF, HALF_H), (OF, 1))

    #@unittest.skip
    def test_monster(self):
        points = [(x, y) for x in range(1000) for y in range(1000)]
        points_to_hexagon(points)
