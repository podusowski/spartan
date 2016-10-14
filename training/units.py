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
    elif m > 999:
        return '{0:.2f}km'.format(round(m / 1000, 2))
    else:
        return '{}m'.format(m)


class Volume:
    def __init__(self, reps:int=None, meters:int=None):
        self.reps = reps
        self.meters = meters

        if not self._valid():
            raise ValueError("one of reps or meters must be set")

    def __str__(self):
        if self.reps is not None:
            return str(self.reps)
        else:
            return km_from_m(self.meters)

    __repr__ = __str__

    def __eq__(self, other):
        return self.reps == other.reps and self.meters == other.meters

    def __add__(self, other):
        if self.reps is not None:
            return Volume(reps=self.reps + other.reps)
        else:
            return Volume(meters=self.meters + other.meters)

    def _valid(self):
        return (self.reps is None) != (self.meters is None)
