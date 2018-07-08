from django.conf.urls import include, url
from django.contrib import admin
from django.conf.urls.static import static

from . import settings

urlpatterns = [
    url('^', include('training.urls')),
    url('^admin/', admin.site.urls),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
