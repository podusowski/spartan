from training import models


def workout(user, name):
    source = models.Gpx.objects.filter(workout__user=user, name=name)

    if not source:
        return {}

    return {'total workouts': source.count()}
