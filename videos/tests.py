from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Video
import os

class VideoViewsTestCase(APITestCase):
    def setUp(self):
        self.test_video = Video.objects.create(
            title='Test Video',
            description='Test Description',
            genre='Test Genre',
            video_file='videos/test_video.mp4'
        )
        # Create necessary directories and files for testing
        video_dir = os.path.join(os.path.dirname(__file__), 'media', 'videos')
        os.makedirs(video_dir, exist_ok=True)
        with open(os.path.join(video_dir, 'test_video.mp4'), 'wb') as f:
            f.write(b'Test video content')

    def tearDown(self):
        # Remove test video file
        video_dir = os.path.join(os.path.dirname(__file__), 'media', 'videos')
        os.remove(os.path.join(video_dir, 'test_video.mp4'))
        os.rmdir(video_dir)

    def test_videoflix_board(self):
        url = reverse('videoflix-board')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('test_video.jpg', response.data)

    def test_download_image(self):
        image_name = 'test_video.jpg'
        url = reverse('download-image', kwargs={'image_name': image_name})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('title', response.data)
        self.assertIn('description', response.data)
        self.assertIn('image_url', response.data)

    def test_download_image_not_found(self):
        image_name = 'nonexistent_image.jpg'
        url = reverse('download-image', kwargs={'image_name': image_name})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_video(self):
        video_name = 'test_video'
        url = reverse('get-video', kwargs={'video_name': video_name})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('1080p', response.data)
        self.assertIn('720p', response.data)
        self.assertIn('480p', response.data)

    def test_get_video_not_found(self):
        video_name = 'nonexistent_video'
        url = reverse('get-video', kwargs={'video_name': video_name})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
