from copy import copy


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


def _format_duration(secs):
    mins = secs // 60
    if mins > 0:
        return "{}min".format(mins)
    else:
        return "{}sec".format(secs)


class Volume:
    class Type:
        DISTANCE = 1
        REPS = 2
        DURATION = 3

    MULTIPLIERS = {Type.DISTANCE: 1000,
                   Type.REPS: 1,
                   Type.DURATION: 60}

    def __init__(self, reps:int=None, meters:int=None, seconds:int=None) -> None:
        if reps is not None:
            self.type = Volume.Type.REPS
            self.value = reps
        elif meters is not None:
            self.type = Volume.Type.DISTANCE
            self.value = meters
        elif seconds is not None:
            self.type = Volume.Type.DURATION
            self.value = seconds
        else:
            self.value = None

    def __str__(self):
        if self.type == Volume.Type.DISTANCE:
            return km_from_m(self.value)
        elif self.type == Volume.Type.REPS:
            return str(self.value)
        elif self.type == Volume.Type.DURATION:
            return _format_duration(self.value)
        else:
            return '-'

    def __repr__(self):
        if self.type == Volume.Type.DISTANCE:
            return "Volume(meters={})".format(self.value)
        elif self.type == Volume.Type.REPS:
            return "Volume(reps={})".format(self.value)
        elif self.type == Volume.Type.DURATION:
            return "Volume(seconds={})".format(self.value)

    def __eq__(self, other):
        if isinstance(other, Volume):
            return self.__dict__ == other.__dict__
        elif isinstance(other, MultiVolume):
            return other == self

    def __add__(self, other):
        if isinstance(other, Volume):
            return self._make_new(self.value + other.value)
        else:
            return other + self

    @property
    def _multiplier(self):
        return Volume.MULTIPLIERS[self.type]

    def left_to(self, goal: int) -> str:
        new = goal * self._multiplier - self.value
        val = self._make_new(abs(new))

        if new > 0:
            return "{} left".format(val)
        else:
            return "done"

    def number(self):
        return self.value / self._multiplier

    def _make_new(self, value):
        ret = copy(self)
        ret.value = value
        return ret


class MultiVolume:
    def __init__(self, volumes=None):
        self.volumes = {}
        if volumes is not None:
            for volume in volumes:
                if volume.type in self.volumes:
                    self.volumes[volume.type] += volume
                else:
                    self.volumes[volume.type] = volume

    def __str__(self):
        if self.volumes:
            return ', '.join([str(volume) for _, volume in self.volumes.items()])
        else:
            return '-'

    __repr__ = __str__

    def __eq__(self, other):
        if isinstance(other, MultiVolume):
            return self.__dict__ == other.__dict__
        elif isinstance(other, Volume) and len(self.volumes) == 1:
            return next(iter(self.volumes.values())) == other

    def __add__(self, other):
        if isinstance(other, Volume):
            return MultiVolume(list(self.volumes.values()) + [other])
        elif isinstance(other, MultiVolume):
            return MultiVolume(list(self.volumes.values()) + list(other.volumes.values()))

        raise TypeError('can\'t add {} and {}'.format(self.__class__, other.__class__))
