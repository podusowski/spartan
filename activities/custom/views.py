from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from training import models
from . import activity


@login_required
def workout(request, workout_id):
    workout = get_object_or_404(models.Workout, pk=workout_id, user=request.user)
    return render(request, 'custom/workout.html', {'workout': workout})


@login_required
def start_workout(request):
    workout = models.Workout.objects.create(user=request.user, activity_type=activity.TYPE)
    return activity.redirect_to_workout(workout)
