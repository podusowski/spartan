import django.utils.timezone

from training import models


def start_workout(user):
    workout = models.Workout.objects.create(user=user)
    return workout.id


def finish_workout(request, workout_id):
    workout = models.Workout.objects.get(pk=workout_id)
    workout.finish()
    workout.save()

    current_excercise = workout.excercise_set.order_by('-pk')[0]
    current_excercise.time_finished = django.utils.timezone.now()
    current_excercise.save()


def add_excercise(user, workout_id, name):
    workout = models.Workout.objects.get(pk=workout_id, user=user)

    try:
        current_excercise = workout.excercise_set.order_by('-pk')[0]
        current_excercise.time_finished = django.utils.timezone.now()
        current_excercise.save()
    except:
        pass

    excercise = workout.excercise_set.create(name=name)
    try:
        workout.start()
    except:
        pass
    workout.save()

    excercise.time_started = django.utils.timezone.now()
    excercise.save()
