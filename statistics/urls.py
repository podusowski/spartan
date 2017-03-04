from django.conf.urls import url, include

from . import views


urlpatterns = [
    url('^statistics$', views.statistics, name='statistics'),
    url('^statistics_this_month$', views.statistics_this_month, name='statistics_this_month'),
    url('^goals$', views.goals, name='goals'),
    url('^add_goal$', views.add_goal, name='add_goal'),
    url('^delete_goal$', views.delete_goal, name='delete_goal'),
    url('^workout/(?P<name>.+)$', views.workout, name='workout_statistics'),
]
