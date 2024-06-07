from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static
from videoflix import settings
from users.views import (
    LoginView,
    DeleteView,
    CustomRegistrationView,
    ActivationView,
    UserDetailView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
    SetNewPassword
)
from videos.views import VideoflixBoard, download_image, get_video

urlpatterns = [
    path('admin/', admin.site.urls),
    path('videoflix/', VideoflixBoard.as_view()),
    path('password-reset/', PasswordResetRequestView.as_view()),
    path('reset-password/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('api/reset-password/', SetNewPassword.as_view()),
    path('download-image/<str:image_name>/', download_image, name='download_image'),
    path('django-rq/', include('django_rq.urls')),
    path('login/', LoginView.as_view()),
    path('register/', CustomRegistrationView.as_view(), name='custom_register'),
    path('kanban/<int:pk>/delete/', DeleteView.as_view()),
    path('accounts/activate/<str:activation_key>/', ActivationView.as_view(), name='django_registration_activate'),
    path('accounts/', include('django_registration.backends.activation.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('videos/<str:video_name>/', get_video),
    path('user/', UserDetailView.as_view()),
    path('api-auth/', include('rest_framework.urls')),  # Hinzufügen für Django REST Framework Auth
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
