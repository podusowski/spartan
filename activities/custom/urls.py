from django.conf.urls import url, include
from . import views


urlpatterns = [
    url('^workout/(?P<workout_id>[0-9]+)/$', views.workout, name='show_custom_workout'),
    url('^add_workout$', views.start_workout, name='add-custom-workout'),
]
