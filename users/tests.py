from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from .models import CustomUser
from .serializers import UserSerializer
from rest_framework.authtoken.models import Token


class UserSerializerTest(TestCase):
    def setUp(self):
        self.user_attributes = {
            'username': 'testuser',
            'password': 'testpassword123',
            'email': 'testuser@example.com',
            'custom': 'custom_value',
            'address': '123 Test St',
            'phone': '1234567890',
        }
        self.user = CustomUser.objects.create(**self.user_attributes)
        self.serializer = UserSerializer(instance=self.user)

    def test_contains_expected_fields(self):
        data = self.serializer.data
        self.assertEqual(set(data.keys()), set(['id', 'custom', 'address', 'phone']))

    def test_custom_field_content(self):
        data = self.serializer.data
        self.assertEqual(data['custom'], self.user_attributes['custom'])

    def test_address_field_content(self):
        data = self.serializer.data
        self.assertEqual(data['address'], self.user_attributes['address'])

    def test_phone_field_content(self):
        data = self.serializer.data
        self.assertEqual(data['phone'], self.user_attributes['phone'])


class UserAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            username='testuser',
            password='testpassword123',
            email='testuser@example.com'
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def test_login_view(self):
        url = reverse('login')
        data = {
            'username': 'testuser',
            'password': 'testpassword123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertIn('user_id', response.data)
        self.assertIn('email', response.data)

    def test_user_detail_view(self):
        url = reverse('user-detail')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], self.user.first_name)
        self.assertEqual(response.data['last_name'], self.user.last_name)
        self.assertEqual(response.data['address'], self.user.address)
        self.assertEqual(response.data['phone'], self.user.phone)

    def test_register_view(self):
        url = reverse('custom_register')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpassword123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'User created successfully. Please check your email to activate your account.')
        new_user = CustomUser.objects.get(username='newuser')
        self.assertFalse(new_user.is_active)

    def test_activation_view(self):
        user = CustomUser.objects.create_user(
            username='inactiveuser',
            password='testpassword123',
            email='inactiveuser@example.com',
            is_active=False
        )
        user.save()
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        activation_key = f"{uid.decode()}-{token}"
        url = reverse('django_registration_activate', kwargs={'activation_key': activation_key})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertTrue(user.is_active)

    def test_password_reset_request_view(self):
        url = reverse('password_reset')
        data = {'email': self.user.email}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Password reset email sent.')

    def test_password_reset_confirm_view(self):
        uid = urlsafe_base64_encode(force_bytes(self.user.pk)).decode()
        token = default_token_generator.make_token(self.user)
        url = reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)  # assuming it redirects

    def test_set_new_password_view(self):
        uid = urlsafe_base64_encode(force_bytes(self.user.pk)).decode()
        token = default_token_generator.make_token(self.user)
        url = reverse('set_new_password')
        data = {
            'uid': uid,
            'token': token,
            'new_password': 'newpassword123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Password has been reset successfully')
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpassword123'))

    def test_put_view(self):
        url = reverse('put-view', kwargs={'pk': self.user.pk})
        data = {
            'custom': 'updated_value',
            'address': 'updated address',
            'phone': '9876543210'
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.custom, 'updated_value')
        self.assertEqual(self.user.address, 'updated address')
        self.assertEqual(self.user.phone, '9876543210')

    def test_delete_view(self):
        url = reverse('delete-view', kwargs={'pk': self.user.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(CustomUser.DoesNotExist):
            CustomUser.objects.get(pk=self.user.pk)
