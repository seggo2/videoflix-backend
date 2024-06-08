from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import CustomUser

class UserAPITest(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email='testuser@example.com', password='password123', username='testuser'
        )
        self.user.is_active = True
        self.user.save()

    def test_login_view_success(self):
        url = reverse('login')
        data = {'username': 'testuser', 'password': 'password123'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertIn('user_id', response.data)
        self.assertIn('email', response.data)

    def test_login_view_failure(self):
        url = reverse('login')
        data = {'username': 'wronguser', 'password': 'wrongpassword'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'Username or password are incorrect')

    def test_user_detail_view(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('user-detail')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.user.email)

    def test_delete_view(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('delete-view', kwargs={'pk': self.user.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
