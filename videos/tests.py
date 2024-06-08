from django.urls import reverse
from rest_framework.test import APITestCase
from users.models import CustomUser
from videos.models import Video
import os
from django.conf import settings
import shutil


class UserAPITest(APITestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(email='testuser@example.com', password='password123')
        self.user.first_name = 'First'
        self.user.save()

    def test_login_view(self):
        url = reverse('login')
        data = {'email': 'testuser@example.com', 'password': 'password123'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.data)

    def test_put_view(self):
        url = reverse('put-view', kwargs={'pk': self.user.pk})
        data = {'first_name': 'UpdatedFirstName'}
        self.client.force_authenticate(user=self.user)
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['first_name'], 'UpdatedFirstName')


class VideoViewsTestCase(APITestCase):

    def setUp(self):
        self.test_video = Video.objects.create(
            title='Test video',
            description='Test description',
            genre='Test genre',
            video_file='videos/Test_video.mp4'
        )
        video_dir = os.path.join(settings.MEDIA_ROOT, 'videos')
        os.makedirs(video_dir, exist_ok=True)
        with open(os.path.join(video_dir, 'Test_video.jpg'), 'wb') as f:
            f.write(b'test image content')

    def tearDown(self):
        video_dir = os.path.join(settings.MEDIA_ROOT, 'videos')
        shutil.rmtree(video_dir)

    def test_videoflix_board(self):
        url = reverse('videoflix-board')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        images = [img.split('_')[0] + '.jpg' for img in response.json()]
        self.assertIn('Test_video.jpg', images)

    def test_download_image(self):
        url = reverse('download-image', kwargs={'image_name': 'Test_video.jpg'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('title', response.data)
        self.assertIn('description', response.data)
        self.assertIn('image_url', response.data)

    def test_get_video(self):
        url = reverse('get-video', kwargs={'video_name': 'Test_video.mp4'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('1080p', response.json())
        self.assertIn('720p', response.json())
        self.assertIn('480p', response.json())
