from training import models


def supported(workout_id):
    return False


def redirect_to_workout(workout_id):
    return redirect('workout', workout_id)
