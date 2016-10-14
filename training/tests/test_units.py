from training import units
from django.test import TestCase
from training.units import Volume


class UnitsTestCase(TestCase):
    def test_constructing(self):
        units.Volume(reps=10)
        units.Volume(meters=10)

        with self.assertRaises(ValueError):
            units.Volume()

        with self.assertRaises(ValueError):
            units.Volume(reps=10, meters=10)

    def test_str(self):
        self.assertEqual("1", str(units.Volume(reps=1)))
        self.assertEqual("999m", str(units.Volume(meters=999)))
        self.assertEqual("1.00km", str(units.Volume(meters=1000)))
        self.assertEqual("15.12km", str(units.Volume(meters=15123)))

    def test_adding(self):
        self.assertEqual(Volume(reps=3), Volume(reps=1) + Volume(reps=2))
        self.assertEqual(Volume(meters=3), Volume(meters=1) + Volume(meters=2))

    def test_pace_convertion_from_mps_to_mpkm(self):
        self.assertEqual('3:59min/km', units.mpkm_from_mps(4.17))
        self.assertEqual('5:03min/km', units.mpkm_from_mps(3.3))
        self.assertEqual('-', units.mpkm_from_mps(0))
