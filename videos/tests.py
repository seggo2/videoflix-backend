from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Video
import os

class VideoViewsTestCase(APITestCase):

    def test_download_image_not_found(self):
        image_name = 'test_video.jpg'
        url = reverse('download-image', kwargs={'image_name': image_name})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_video_not_found(self):
        video_name = 'nonexistent_video'
        url = reverse('get-video', kwargs={'video_name': video_name})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
