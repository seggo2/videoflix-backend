from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from users.models import CustomUser

class UserAPITest(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email='testuser@example.com',
            password='password123',
            username='testuser'
        )
        self.client.force_authenticate(user=self.user)

    def test_login_view(self):
        url = reverse('login')
        data = {'username': 'testuser@example.com', 'password': 'password123'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

    def test_user_detail_view(self):
        url = reverse('user-detail')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.user.email)
