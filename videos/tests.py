import os
from django.conf import settings
from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Video


class VideoViewsTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.test_video = Video.objects.create(
            title="Test Video",
            description="Test Description",
            genre="Test Genre",
            video_file=SimpleUploadedFile("test_video.mp4", b"file_content", content_type="video/mp4")
        )
        self.test_image = SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg")
        video_dir = os.path.join(settings.MEDIA_ROOT, 'videos')
        if not os.path.exists(video_dir):
            os.makedirs(video_dir)
        with open(os.path.join(video_dir, self.test_video.video_file.name), 'wb') as f:
            f.write(b"file_content")
        with open(os.path.join(video_dir, "test_image.jpg"), 'wb') as f:
            f.write(b"file_content")

    def tearDown(self):
        self.test_video.delete()
        video_dir = os.path.join(settings.MEDIA_ROOT, 'videos')
        os.remove(os.path.join(video_dir, self.test_video.video_file.name))
        os.remove(os.path.join(video_dir, "test_image.jpg"))

    def test_videoflix_board(self):
        response = self.client.get(reverse('videoflix-board'))
        self.assertEqual(response.status_code, 200)
        self.assertIn("test_image.jpg", response.json())

    def test_download_image(self):
        response = self.client.get(reverse('download_image', args=['test_image.jpg']))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['title'], self.test_video.title)

    def test_download_image_not_found(self):
        response = self.client.get(reverse('download_image', args=['non_existent.jpg']))
        self.assertEqual(response.status_code, 404)

    def test_get_video(self):
        response = self.client.get(reverse('get_video', args=[self.test_video.video_file.name]))
        self.assertEqual(response.status_code, 200)
        self.assertIn('1080p', response.json())
        self.assertIn('720p', response.json())
        self.assertIn('480p', response.json())

    def test_get_video_not_found(self):
        response = self.client.get(reverse('get_video', args=['non_existent.mp4']))
        self.assertEqual(response.status_code, 404)
