from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static
from videoflix import settings
from users.views import (
    LoginView,
    DeleteView,
    CustomRegistrationView,
    ActivationView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
    SetNewPassword,
    PutView,
    CheckUserView,
)
from videos.views import VideoflixBoard, download_image, get_video,VideoUploadView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('videoflix/', VideoflixBoard.as_view(), name='videoflix-board'),
    path('upload-video/', VideoUploadView.as_view(), name='upload-video'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('reset-password/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('api/reset-password/', SetNewPassword.as_view(), name='set-new-password'),
    path('download-image/<str:image_name>/', download_image, name='download-image'),
    path('login/', LoginView.as_view(), name='login'),
    path('register/', CustomRegistrationView.as_view(), name='custom_register'),
    path('check-user/', CheckUserView.as_view(), name='check-user'),
    path('kanban/<int:pk>/delete/', DeleteView.as_view(), name='delete-view'),
    path('accounts/activate/<str:activation_key>/', ActivationView.as_view(), name='activation-view'),
    path('accounts/', include('django_registration.backends.activation.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('videos/<str:video_name>/', get_video, name='get-video'),
    path('django-rq/', include('django_rq.urls')),
    path('put/<int:pk>/', PutView.as_view(), name='put-view'),  # Added PUT view
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
