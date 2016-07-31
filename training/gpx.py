from . import gpxpy

def parse(xml):
    gpx = gpxpy.parse(xml)
    segment = gpx.tracks[0].segments[0]

    moving_time, stopped_time, moving_distance, stopped_distance, max_speed = segment.get_moving_data()

    start_time, end_time = segment.get_time_bounds()

    return {'moving_time': moving_time,
            'length_2d': segment.length_2d(),
            'length_3d': segment.length_3d(),
            'start_time': start_time,
            'end_time': end_time,
            'duration': end_time - start_time}
