
from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static
from videoflix import settings


urlpatterns = [
    path('admin/', admin.site.urls),
    path('django-rq/', include('django_rq.urls')),

] + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
