from django.conf.urls import url

from . import views

urlpatterns = [
    url('^$', views.index, name='index'),
    url('^start_training_session/$', views.start_training_session, name='start_training_session'),
    url('^finish_training_session/(?P<training_session_id>[0-9]+)$', views.finish_training_session, name='finish_training_session'),
    url('^training_session/(?P<training_session_id>[0-9]+)/$', views.training_session, name='training_session'),
    url('^add_excercise/(?P<training_session_id>[0-9]+)/$', views.add_excercise, name='add_excercise'),
    url('^save_excercise/(?P<excercise_id>[0-9]+)/$', views.save_excercise, name='save_excercise'),
]
