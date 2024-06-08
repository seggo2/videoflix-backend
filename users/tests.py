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
    
    def test_activation_view(self):
        activation_key = 'test-activation-key'
        url = reverse('activation-view', kwargs={'activation_key': activation_key})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_login_view(self):
        url = reverse('login')
        data = {'email': 'testuser@example.com', 'password': 'password123'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
    
    def test_put_view(self):
        url = reverse('put-view', kwargs={'pk': self.user.pk})
        data = {'first_name': 'UpdatedFirstName'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'UpdatedFirstName')
