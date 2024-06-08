from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from users.models import CustomUser
from .models import Video

class VideoViewsTestCase(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email='testuser@example.com', password='password123', username='testuser'
        )
        self.client.force_authenticate(user=self.user)
        self.video = Video.objects.create(
            title='Test Video',
            description='Test Description',
            genre='Test',
            video_file='videos/test_video.mp4'
        )

    def test_videoflix_board(self):
        url = reverse('videoflix-board')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Test Video', response.json())

    def test_download_image(self):
        url = reverse('download-image', kwargs={'image_name': 'test_video.jpg'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_video(self):
        url = reverse('get-video', kwargs={'video_name': 'test_video.mp4'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
