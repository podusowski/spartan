import logging

import django.utils.timezone

from training import models


def start_workout(user):
    workout = models.Workout.objects.create(user=user)
    return workout.id


def _finish_active_excercise(workout):
    try:
        current_excercise = workout.excercise_set.latest('pk')
        current_excercise.time_finished = django.utils.timezone.now()
        current_excercise.save()
    except models.Excercise.DoesNotExist:
        logging.debug("nothing to finish - no active excercise yet")


def finish_workout(request, workout_id):
    workout = models.Workout.objects.get(pk=workout_id)
    workout.finish()
    workout.save()

    _finish_active_excercise(workout)


def add_excercise(user, workout_id, name):
    workout = models.Workout.objects.get(pk=workout_id, user=user)

    _finish_active_excercise(workout)

    excercise = workout.excercise_set.create(name=name)
    try:
        workout.start()
    except:
        pass
    workout.save()

    excercise.time_started = django.utils.timezone.now()
    excercise.save()
