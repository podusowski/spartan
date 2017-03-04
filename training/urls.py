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

    url('^user_profile$', views.user_profile, name='user_profile'),

    url('^statistics/', include('statistics.urls')),

    url('^strength/', include('activities.strength.urls')),
    url('^gps/', include('activities.gps.urls')),

    url('^dashboard$', views.dashboard, name='dashboard'),
    url('^delete_workout/(?P<workout_id>[0-9]+)/$', views.delete_workout, name='delete_workout'),
    url('^workout/(?P<training_session_id>[0-9]+)/$', views.workout, name='workout'),
    url('^explorer/$', views.explorer, name='explorer'),
]
