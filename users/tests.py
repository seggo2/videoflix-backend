from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from .models import CustomUser
from .serializers import UserSerializer
from rest_framework.test import APITestCase, APIClient


class UserSerializerTest(APITestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='testuser',
            password='testpassword',
            custom='Custom info',
            address='123 Main St',
            phone='1234567890'
        )
        self.serializer = UserSerializer(instance=self.user)

    def test_contains_expected_fields(self):
        data = self.serializer.data
        self.assertEqual(set(data.keys()), {'id', 'custom', 'address', 'phone', 'author_name'})

    def test_custom_field_content(self):
        data = self.serializer.data
        self.assertEqual(data['custom'], 'Custom info')

    def test_address_field_content(self):
        data = self.serializer.data
        self.assertEqual(data['address'], '123 Main St')

    def test_phone_field_content(self):
        data = self.serializer.data
        self.assertEqual(data['phone'], '1234567890')

class UserAPITest(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            username='testuser',
            password='testpassword',
            email='testuser@example.com'
        )
        self.user.is_active = True
        self.user.save()

    def test_login_view(self):
        url = reverse('login')
        data = {
            'username': 'testuser',
            'password': 'testpassword'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

    def test_user_detail_view(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('UserDetailView')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], '')
        self.assertEqual(response.data['last_name'], '')

    def test_register_view(self):
        url = reverse('CustomRegistrationView')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpassword'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['message'], 'User created successfully. Please check your email to activate your account.')

    def test_activation_view(self):
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)
        activation_key = f"{uid}-{token}"
        url = reverse('ActivationView', kwargs={'activation_key': activation_key})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_password_reset_request_view(self):
        url = reverse('PasswordResetRequestView')
        data = {'email': 'testuser@example.com'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['message'], 'Password reset email sent.')

    def test_password_reset_confirm_view(self):
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)
        url = reverse('PasswordResetConfirmView', kwargs={'uidb64': uid, 'token': token})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    def test_set_new_password_view(self):
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)
        url = reverse('SetNewPassword')
        data = {
            'uid': uid,
            'token': token,
            'new_password': 'newpassword'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['message'], 'Password has been reset successfully')

    def test_put_view(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('put-view', kwargs={'pk': self.user.pk})
        data = {
            'first_name': 'UpdatedName'
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'UpdatedName')

    def test_delete_view(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('DeleteView', kwargs={'pk': self.user.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)