def mpkm_from_mps(m_per_s):
    try:
        c = 16.666666666667
        mpkm = int(c // m_per_s)
        spkm = int((c / m_per_s - mpkm) * 60)
        return '{}:{:02d}min/km'.format(mpkm, spkm)
    except:
        return '-'

def km_from_m(m):
    if m is None:
        return None
    elif m > 100000:
        return '{}km'.format(round(m / 1000))
    elif m > 999:
        return '{0:.2f}km'.format(round(m / 1000, 2))
    else:
        return '{}m'.format(m)


class Volume:
    def __init__(self, reps:int=None, meters:int=None) -> None:
        self.distance = meters is not None
        self.multiplier = 1000 if self.distance else 1
        self.value = meters if self.distance else reps

    def __str__(self):
        if self.distance:
            return km_from_m(self.value)
        else:
            return str(self.value)

    __repr__ = __str__

    def __eq__(self, other):
        return self.value == other.value

    def __add__(self, other):
        return self._make_new(self.value + other.value)

    def left_to(self, goal: int) -> str:
        new = goal * self.multiplier - self.value
        val = self._make_new(abs(new))

        if new > 0:
            return "{} left".format(val)
        else:
            return "done"

    def number(self):
        return self.value / self.multiplier

    def _make_new(self, value):
        return Volume(meters=value) if self.distance else Volume(reps=value)
