
from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static
from videoflix import settings
from users.views import LoginView,put,delete,CustomRegistrationView,ActivationView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('django-rq/', include('django_rq.urls')),
    path('login/', LoginView.as_view()),
    path('register/', CustomRegistrationView.as_view(), name='custom_register'),  
    path('kanban/<int:pk>/delete/', delete.as_view()),
    path('accounts/', include('django_registration.backends.activation.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/activate/<str:activation_key>/', ActivationView.as_view(), name='django_registration_activate'),

] + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
