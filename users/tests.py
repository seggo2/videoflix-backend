from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import CustomUser


class UserAPITest(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email='testuser@example.com', password='password123', username='testuser'
        )
        self.client.force_authenticate(user=self.user)

    def test_login_view(self):
        url = reverse('login')
        data = {'username': 'testuser', 'password': 'password123'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_detail_view(self):
        url = reverse('user-detail')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.user.email)

    def test_delete_view(self):
        url = reverse('delete-view', kwargs={'pk': self.user.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
