def mpkm_from_mps(m_per_s):
    try:
        return '{}min/km'.format(round(16.666666666667 / m_per_s, 2))
    except:
        return '-'

def km_from_m(m):
    if m > 1000:
        return '{}km'.format(round(m / 1000, 2))
    else:
        return '{}m'.format(m)
