from training import models


def start_workout(user):
    workout = models.Workout.objects.create(user=user)
    return workout.id
