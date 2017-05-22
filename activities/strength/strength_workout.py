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


def add_reps(user, excercise_id, reps):
    s = models.Excercise.objects.get(pk=excercise_id, workout__user=user)
    s.reps_set.create(reps=reps)

    s.time_updated = django.utils.timezone.now()
    s.save()
    return s.workout.id


def start_timer(user, excercise_id):
    excercise = models.Excercise.objects.get(pk=excercise_id, workout__user=user)
    excercise.timers_set.create(time_started=django.utils.timezone.now())
    return excercise.workout.id


def stop_timer(user, excercise_id):
    excercise = models.Excercise.objects.get(pk=excercise_id, workout__user=user)
    timer = excercise.timers_set.latest('pk')
    timer.time_finished = django.utils.timezone.now()
    timer.save()
    return excercise.workout.id


def undo(user, workout_id):
    workout = models.Workout.objects.get(pk=workout_id, user=user)

    if workout.excercise_set.count() == 0:
        return

    current_excercise = workout.excercise_set.latest('pk')

    if current_excercise.reps_set.count() > 0:
        latest_set = current_excercise.reps_set.latest('pk')
        latest_set.delete()
    else:
        current_excercise.delete()
