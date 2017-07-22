from django.conf.urls import url, include

from . import views


urlpatterns = [
    url('^workout/(?P<workout_id>[0-9]+)/$', views.workout, 'show_strength_workout'),
    url('^start_workout/$', views.start_workout, name='start_workout'),
    url('^finish_workout/(?P<training_session_id>[0-9]+)$', views.finish_workout, name='finish_workout'),
    url('^add_excercise/(?P<training_session_id>[0-9]+)/$', views.add_excercise, name='add_excercise'),
    url('^add_reps/(?P<excercise_id>[0-9]+)/$', views.add_reps, name='add_reps'),
    url('^start_timer/(?P<excercise_id>[0-9]+)$', views.start_timer, name='start_timer'),
    url('^stop_timer/(?P<excercise_id>[0-9]+)$', views.stop_timer, name='stop_timer'),
    url('^undo/(?P<workout_id>[0-9]+)$', views.undo, name='undo'),
]
