from .models import *


def previous_workouts(request):
    return Workout.objects.filter(user=request.user).order_by('-pk')
