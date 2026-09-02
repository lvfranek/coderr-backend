# Third-party
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

# Local imports
from profile_app.models import UserProfile


class RegistrationTests(APITestCase):
    """Tests for POST /api/registration/"""

    def setUp(self):
        self.url = '/api/registration/'
        self.valid_payload = {
            'username': 'newuser',
            'email': 'newuser@mail.de',
            'password': 'testpass123',
            'repeated_password': 'testpass123',
            'type': 'customer',
        }

    def test_registration_success(self):
        response = self.client.post(self.url, self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
        self.assertTrue(User.objects.filter(username='newuser').exists())
        self.assertTrue(UserProfile.objects.filter(user__username='newuser').exists())

    def test_registration_password_mismatch(self):
        payload = self.valid_payload.copy()
        payload['repeated_password'] = 'different'
        response = self.client.post(self.url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_duplicate_username(self):
        User.objects.create_user(username='newuser', password='x')
        response = self.client.post(self.url, self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_duplicate_email(self):
        User.objects.create_user(username='other', email='newuser@mail.de', password='x')
        response = self.client.post(self.url, self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoginTests(APITestCase):
    """Tests for POST /api/login/"""

    def setUp(self):
        self.url = '/api/login/'
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        UserProfile.objects.create(user=self.user, type='customer')

    def test_login_success(self):
        response = self.client.post(
            self.url, {'username': 'testuser', 'password': 'testpass123'}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

    def test_login_wrong_password(self):
        response = self.client.post(
            self.url, {'username': 'testuser', 'password': 'wrongpass'}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_unknown_user(self):
        response = self.client.post(
            self.url, {'username': 'ghost', 'password': 'whatever'}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
