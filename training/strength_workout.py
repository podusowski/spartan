from training import models


def start_workout(user):
    workout = models.Workout.objects.create(user=user)
    return workout.id


def finish_workout(request, workout_id):
    workout = models.Workout.objects.get(pk=workout_id)
    workout.finish()
    workout.save()

    try:
        current_excercise = workout.excercise_set.order_by('-pk')[0]
        current_excercise.time_finished = timezone.now()
        current_excercise.save()
    except:
        pass
