from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from .models import CustomUser

class UserAPITest(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='testuser', email='test@example.com', password='testpassword'
        )
        self.user.activation_token = default_token_generator.make_token(self.user)
        self.user.save()
        self.client.force_authenticate(user=self.user)

    def test_login_view(self):
        url = reverse('login')
        data = {'username': 'testuser', 'password': 'testpassword'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # self.assertIn('token', response.json())


    def test_user_detail_view(self):
        url = reverse('user-detail')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['first_name'], self.user.first_name)
        self.assertEqual(response.json()['last_name'], self.user.last_name)

    def test_register_view(self):
        url = reverse('custom_register')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpassword'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.json())

    def test_activation_view(self):
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)
        activation_key = f"{uid}-{token}"
        url = reverse('activation-view', kwargs={'activation_key': activation_key})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Thank You', response.content.decode())

    def test_password_reset_request_view(self):
        url = reverse('password-reset-request')
        data = {'email': self.user.email}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.json())

    def test_password_reset_confirm_view(self):
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)
        url = reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)  # It should redirect

    def test_set_new_password_view(self):
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)
        url = reverse('set-new-password')
        data = {
            'uid': uid,
            'token': token,
            'new_password': 'newpassword123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.json())

    def test_put_view(self):
        url = reverse('put-view', kwargs={'pk': self.user.pk})
        data = {
            'first_name': 'UpdatedFirstName',
            'last_name': 'UpdatedLastName',
            'address': 'New Address',
            'phone': '123456789'
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['first_name'], 'UpdatedFirstName')
        self.assertEqual(response.json()['last_name'], 'UpdatedLastName')

    def test_delete_view(self):
        url = reverse('delete-view', kwargs={'pk': self.user.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
