# Third-party
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

# Local imports
from offers_app.models import Offer
from profile_app.models import UserProfile
from reviews_app.models import Review


class BaseInfoTests(APITestCase):
    """Tests for GET /api/base-info/"""

    def setUp(self):
        self.url = '/api/base-info/'

    def test_base_info_accessible_without_auth(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_base_info_returns_correct_structure(self):
        response = self.client.get(self.url)
        expected_keys = {
            'review_count', 'average_rating', 'business_profile_count', 'offer_count'
        }
        self.assertEqual(set(response.data.keys()), expected_keys)

    def test_base_info_counts_are_correct(self):
        business = User.objects.create_user(username='biz', password='pass123')
        UserProfile.objects.create(user=business, type='business')
        customer = User.objects.create_user(
            username='cust', password='pass123')
        UserProfile.objects.create(user=customer, type='customer')
        Offer.objects.create(user=business, title='Test Offer')
        Review.objects.create(business_user=business,
                              reviewer=customer, rating=4)

        response = self.client.get(self.url)
        self.assertEqual(response.data['business_profile_count'], 1)
        self.assertEqual(response.data['offer_count'], 1)
        self.assertEqual(response.data['review_count'], 1)
        self.assertEqual(response.data['average_rating'], 4.0)
