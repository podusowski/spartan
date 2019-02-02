from django.contrib.auth.decorators import login_required
import training.models


@login_required
def workout(request, workout_id):
    workout = get_object_or_404(training.models.Workout, pk=workout_id, user=request.user)
    return render(request, 'custom/workout.html', {'workout': workout})
