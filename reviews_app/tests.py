# Third-party
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

# Local imports
from profile_app.models import UserProfile
from .models import Review


class ReviewListCreateTests(APITestCase):
    """Tests for GET/POST /api/reviews/"""

    def setUp(self):
        self.customer = User.objects.create_user(
            username='cust', password='pass123')
        UserProfile.objects.create(user=self.customer, type='customer')
        self.business = User.objects.create_user(
            username='biz', password='pass123')
        UserProfile.objects.create(user=self.business, type='business')
        self.url = '/api/reviews/'

    def test_create_review_as_customer_success(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.post(
            self.url, {'business_user': self.business.id,
                       'rating': 4, 'description': 'Good'}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['reviewer'], self.customer.id)

    def test_create_review_as_business_forbidden(self):
        self.client.force_authenticate(user=self.business)
        response = self.client.post(
            self.url, {'business_user': self.business.id,
                       'rating': 4, 'description': 'Good'}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_duplicate_review_fails(self):
        self.client.force_authenticate(user=self.customer)
        self.client.post(
            self.url, {'business_user': self.business.id,
                       'rating': 4, 'description': 'Good'}
        )
        response = self.client.post(
            self.url, {'business_user': self.business.id,
                       'rating': 5, 'description': 'Again'}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_reviews_requires_auth(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_reviews_success(self):
        Review.objects.create(
            business_user=self.business, reviewer=self.customer, rating=5, description='Great'
        )
        self.client.force_authenticate(user=self.customer)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_filter_reviews_by_business_user(self):
        Review.objects.create(
            business_user=self.business, reviewer=self.customer, rating=5, description='Great'
        )
        self.client.force_authenticate(user=self.customer)
        response = self.client.get(
            self.url, {'business_user': self.business.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


class ReviewUpdateDeleteTests(APITestCase):
    """Tests for PATCH/DELETE /api/reviews/{id}/"""

    def setUp(self):
        self.customer = User.objects.create_user(
            username='cust', password='pass123')
        UserProfile.objects.create(user=self.customer, type='customer')
        self.other_customer = User.objects.create_user(
            username='cust2', password='pass123')
        UserProfile.objects.create(user=self.other_customer, type='customer')
        self.business = User.objects.create_user(
            username='biz', password='pass123')
        UserProfile.objects.create(user=self.business, type='business')
        self.review = Review.objects.create(
            business_user=self.business, reviewer=self.customer, rating=4, description='Good'
        )
        self.url = f'/api/reviews/{self.review.id}/'

    def test_patch_own_review_success(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.patch(self.url, {'rating': 5})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_patch_others_review_forbidden(self):
        self.client.force_authenticate(user=self.other_customer)
        response = self.client.patch(self.url, {'rating': 1})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_own_review_success(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_others_review_forbidden(self):
        self.client.force_authenticate(user=self.other_customer)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
