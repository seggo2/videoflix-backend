
from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static
from videoflix import settings
from users.views import LoginView,delete,CustomRegistrationView,ActivationView,UserDetailView
from videos.views import VideoflixBoard,download_image


urlpatterns = [
    path('admin/', admin.site.urls),
    path('videoflix/', VideoflixBoard.as_view()),
    path('download-image/<str:image_name>/', download_image, name='download_image'),
    path('django-rq/', include('django_rq.urls')),
    path('login/', LoginView.as_view()),
    path('register/', CustomRegistrationView.as_view(), name='custom_register'),  
    path('kanban/<int:pk>/delete/', delete.as_view()),
    path('accounts/activate/<str:activation_key>/', ActivationView.as_view(), name='django_registration_activate'),
    path('accounts/', include('django_registration.backends.activation.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('user/', UserDetailView.as_view(), name='user_detail'),


] + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
