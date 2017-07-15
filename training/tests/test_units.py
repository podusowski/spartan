from training import units
from training.units import *
from django.test import TestCase
from training.units import Volume


class UnitsTestCase(TestCase):
    def test_constructing(self):
        units.Volume(reps=10)
        units.Volume(meters=10)

    def test_str(self):
        self.assertEqual("1", str(units.Volume(reps=1)))
        self.assertEqual("999m", str(units.Volume(meters=999)))
        self.assertEqual("1.00km", str(units.Volume(meters=1000)))
        self.assertEqual("15.12km", str(units.Volume(meters=15123)))

    def test_goal(self):
        self.assertEqual("done", units.Volume(reps=1).left_to(1))
        self.assertEqual("done", units.Volume(reps=2).left_to(1))

        # for distance, we treat number as km
        self.assertEqual("done", units.Volume(meters=1000).left_to(1))

        self.assertEqual("1 left", units.Volume(reps=1).left_to(2))
        self.assertEqual("1.00km left", units.Volume(meters=1000).left_to(2))

    def test_adding(self):
        self.assertEqual(Volume(reps=3), Volume(reps=1) + Volume(reps=2))
        self.assertEqual(Volume(meters=3), Volume(meters=1) + Volume(meters=2))

    def test_duration_volume(self):
        self.assertEqual("1sec", str(units.Volume(seconds=1)))
        self.assertEqual("1min", str(units.Volume(seconds=60)))

        self.assertEqual("1min left", units.Volume(seconds=60).left_to(2))

    def test_pace_convertion_from_mps_to_mpkm(self):
        self.assertEqual('3:59min/km', units.mpkm_from_mps(4.17))
        self.assertEqual('5:03min/km', units.mpkm_from_mps(3.3))
        self.assertEqual('-', units.mpkm_from_mps(0))

    def test_multivolume(self):
        empty = MultiVolume()
        self.assertEqual('-', str(empty))

        reps_and_time = MultiVolume([Volume(reps=1), Volume(seconds=2)])
        self.assertEqual('1, 2sec', str(reps_and_time))

    def test_adding_multivolume(self):
        reps = MultiVolume() + Volume(reps=1)
        self.assertEqual('1', str(reps))

        reps = Volume(reps=1) + MultiVolume()
        self.assertEqual('1', str(reps))

        reps = MultiVolume() + Volume(reps=1) + Volume(reps=1)
        self.assertEqual('2', str(reps))

        reps = MultiVolume() + Volume(reps=1) + Volume(seconds=1)
        self.assertEqual('1, 1sec', str(reps))

        reps = MultiVolume([Volume(reps=1)]) + MultiVolume([Volume(seconds=1)])
        self.assertEqual('1, 1sec', str(reps))

        with self.assertRaises(TypeError):
            MultiVolume() + 1

    def test_compare_multivalue(self):
        self.assertEqual(MultiVolume([Volume(reps=1)]), MultiVolume([Volume(reps=1)]))

        self.assertNotEqual(MultiVolume([Volume(reps=1)]), MultiVolume([Volume(seconds=1)]))
        self.assertNotEqual(MultiVolume([Volume(reps=1)]), MultiVolume([Volume(reps=2)]))

        self.assertEqual(MultiVolume([Volume(reps=1)]), Volume(reps=1))
        self.assertEqual(Volume(reps=1), MultiVolume([Volume(reps=1)]))

        self.assertNotEqual(MultiVolume([Volume(reps=1), Volume(seconds=1)]), Volume(reps=1))
