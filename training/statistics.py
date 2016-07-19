from .models import *


def previous_workouts(request):
    return Workout.objects.filter(user=request.user).order_by('-pk')


def most_common_excercises(request):
    return Excercise.objects.filter(workout__user=request.user).values_list('name').annotate(count=Count('name')).order_by('-count')
