def mpkm_from_mps(m_per_s):
    try:
        c = 16.666666666667
        mpkm = int(c // m_per_s)
        spkm = int((c / m_per_s - mpkm) * 60)
        return '{}:{}min/km'.format(mpkm, spkm)
    except:
        return '-'

def km_from_m(m):
    if m is None:
        return None
    elif m > 1000:
        return '{}km'.format(round(m / 1000, 2))
    else:
        return '{}m'.format(m)
