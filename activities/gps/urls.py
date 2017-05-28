from django.conf.urls import url

from . import views

urlpatterns = [
    url('^upload_gpx/$', views.upload_gpx, name='upload_gpx'),
    url('^endomondo/$', views.endomondo, name='endomondo'),
    url('^disconnect_endomondo/$', views.disconnect_endomondo , name='disconnect_endomondo'),
    url('^synchronize_endomondo/$', views.synchronize_endomondo, name='synchronize_endomondo'),
    url('^synchronize_endomondo_ajax/$', views.synchronize_endomondo_ajax, name='synchronize_endomondo_ajax'),
    url('^purge_endomondo/$', views.purge_endomondo, name='purge_endomondo'),

    url('^workout/(?P<workout_id>[0-9]+)/$', views.workout, name='show_gps_workout'),
]
