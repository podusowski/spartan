from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url('^', include('training.urls')),
    url('^admin/', include(admin.site.urls)),
]
