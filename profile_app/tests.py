# Third-party
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

# Local imports
from .models import UserProfile


class ProfileDetailTests(APITestCase):
    """Tests for GET/PATCH /api/profile/{pk}/"""

    def setUp(self):
        self.owner = User.objects.create_user(
            username='owner', password='pass123')
        self.other = User.objects.create_user(
            username='other', password='pass123')
        self.profile = UserProfile.objects.create(
            user=self.owner, type='business')
        self.url = f'/api/profile/{self.owner.id}/'

    def test_get_profile_requires_auth(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_profile_success(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'owner')

    def test_get_profile_not_found(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.get('/api/profile/9999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_own_profile_success(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.patch(self.url, {'location': 'Berlin'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['location'], 'Berlin')

    def test_patch_other_profile_forbidden(self):
        self.client.force_authenticate(user=self.other)
        response = self.client.patch(self.url, {'location': 'Berlin'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_updates_user_first_name(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.patch(self.url, {'first_name': 'Max'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.owner.refresh_from_db()
        self.assertEqual(self.owner.first_name, 'Max')


class ProfileListTests(APITestCase):
    """Tests for GET /api/profiles/business/ and /api/profiles/customer/"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='someone', password='pass123')
        UserProfile.objects.create(user=self.user, type='business')
        customer_user = User.objects.create_user(
            username='cust', password='pass123')
        UserProfile.objects.create(user=customer_user, type='customer')

    def test_business_list_requires_auth(self):
        response = self.client.get('/api/profiles/business/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_business_list_success(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/profiles/business/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_customer_list_success(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/profiles/customer/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
