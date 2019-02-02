

TYPE = 'custom'


def redirect_to_workout(workout):
    return redirect('show_custom_workout', workout.id)


def volume(workout):
    return 0


def color(workout):
    return 'orange'
