from django.views.generic.edit import CreateView
from django.contrib.auth.forms import UserCreationForm
from django.conf.urls import url, include
from django.urls import path

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
    url('^custom/', include('activities.custom.urls')),

    url('^dashboard$', views.dashboard, name='dashboard'),
    url('^new_dashboard$', views.new_dashboard),
    url('^new_activity$', views.new_activity, name='new_activity'),
    url('^delete_workout/(?P<workout_id>[0-9]+)/$', views.delete_workout, name='delete_workout'),
    url('^workout/(?P<training_session_id>[0-9]+)/$', views.workout, name='workout'),
    path('edit_workout/<int:workout_id>', views.edit_workout, name='edit_workout'),
    url('^explorer/$', views.explorer, name='explorer'),
]
