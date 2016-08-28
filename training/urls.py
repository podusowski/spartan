from django.views.generic.edit import CreateView
from django.contrib.auth.forms import UserCreationForm
from django.conf.urls import url, include

from . import views

urlpatterns = [
    url('^', include('django.contrib.auth.urls')),
    url('^$', views.index, name='index'),

    url('^register/$',
        CreateView.as_view(
            template_name='registration/register.html',
            form_class=UserCreationForm,
            success_url='/'
        ), name='register'),

    url('^dashboard$', views.dashboard, name='dashboard'),
    url('^statistics$', views.statistics, name='statistics'),
    url('^start_workout/$', views.start_workout, name='start_workout'),
    url('^finish_workout/(?P<training_session_id>[0-9]+)$', views.finish_workout, name='finish_workout'),
    url('^delete_workout/(?P<workout_id>[0-9]+)/$', views.delete_workout, name='delete_workout'),
    url('^workout/(?P<training_session_id>[0-9]+)/$', views.workout, name='workout'),
    url('^add_excercise/(?P<training_session_id>[0-9]+)/$', views.add_excercise, name='add_excercise'),
    url('^add_reps/(?P<excercise_id>[0-9]+)/$', views.add_reps, name='add_reps'),
    url('^upload_gpx/$', views.upload_gpx, name='upload_gpx'),
    url('^endomondo/$', views.endomondo, name='endomondo'),
    url('^disconnect_endomondo/$', views.disconnect_endomondo , name='disconnect_endomondo'),
    url('^synchronize_endomondo/$', views.synchronize_endomondo, name='synchronize_endomondo'),
    url('^purge_endomondo/$', views.purge_endomondo, name='purge_endomondo'),
]
