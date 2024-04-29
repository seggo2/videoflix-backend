
from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static
from videoflix import settings
from users.views import LoginView,put,delete,register_view


urlpatterns = [
    path('admin/', admin.site.urls),
    path('django-rq/', include('django_rq.urls')),
    path('login/', LoginView.as_view()),
    path('register/', register_view),
    path('kanban/<int:pk>/put/', put.as_view()),
    path('kanban/<int:pk>/delete/', delete.as_view()),
    
] + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
