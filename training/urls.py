from django.conf.urls import url

from . import views

urlpatterns = [
    url('^$', views.index, name='index'),
    url('^start_workout/$', views.start_workout, name='start_workout'),
    url('^finish_workout/(?P<training_session_id>[0-9]+)$', views.finish_workout, name='finish_workout'),
    url('^training_session/(?P<training_session_id>[0-9]+)/$', views.training_session, name='training_session'),
    url('^add_excercise/(?P<training_session_id>[0-9]+)/$', views.add_excercise, name='add_excercise'),
    url('^save_excercise/(?P<excercise_id>[0-9]+)/$', views.save_excercise, name='save_excercise'),
]
