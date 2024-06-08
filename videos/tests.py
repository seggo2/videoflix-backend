import os
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from users.models import CustomUser
from videos.models import Video

class VideoViewsTestCase(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email='testuser@example.com',
            password='password123',
            username='testuser'
        )
        self.client.force_authenticate(user=self.user)
        self.video = Video.objects.create(
            title='Test Video',
            description='Test Description',
            genre='Test',
            video_file='videos/test_video.mp4'
        )
        # Ensure the test image exists
        if not os.path.exists('media/videos'):
            os.makedirs('media/videos')
        with open('media/videos/test_video.jpg', 'w') as f:
            f.write('')

    def test_videoflix_board(self):
        url = reverse('videoflix-board')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Test Video', response.json())

    def test_download_image(self):
        url = reverse('download-image', kwargs={'image_name': 'test_video.jpg'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
