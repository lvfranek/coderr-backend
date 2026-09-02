# Third-party
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

# Local imports
from profile_app.models import UserProfile
from .models import Offer, OfferDetail


def build_offer_payload(title='Test Offer'):
    return {
        'title': title,
        'description': 'A test offer.',
        'details': [
            {'title': 'Basic', 'revisions': 1, 'delivery_time_in_days': 5,
             'price': 100, 'features': ['A'], 'offer_type': 'basic'},
            {'title': 'Standard', 'revisions': 3, 'delivery_time_in_days': 7,
             'price': 200, 'features': ['A', 'B'], 'offer_type': 'standard'},
            {'title': 'Premium', 'revisions': 10, 'delivery_time_in_days': 10,
             'price': 500, 'features': ['A', 'B', 'C'], 'offer_type': 'premium'},
        ],
    }


class OfferListCreateTests(APITestCase):
    """Tests for GET/POST /api/offers/"""

    def setUp(self):
        self.business_user = User.objects.create_user(
            username='biz', password='pass123')
        UserProfile.objects.create(user=self.business_user, type='business')
        self.customer_user = User.objects.create_user(
            username='cust', password='pass123')
        UserProfile.objects.create(user=self.customer_user, type='customer')
        self.url = '/api/offers/'

    def test_list_offers_public(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_offer_as_business_success(self):
        self.client.force_authenticate(user=self.business_user)
        response = self.client.post(
            self.url, build_offer_payload(), format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(OfferDetail.objects.count(), 3)

    def test_create_offer_as_customer_forbidden(self):
        self.client.force_authenticate(user=self.customer_user)
        response = self.client.post(
            self.url, build_offer_payload(), format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_offer_requires_exactly_three_details(self):
        self.client.force_authenticate(user=self.business_user)
        payload = build_offer_payload()
        payload['details'] = payload['details'][:2]
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_by_creator_id(self):
        self.client.force_authenticate(user=self.business_user)
        self.client.post(self.url, build_offer_payload(), format='json')
        response = self.client.get(
            self.url, {'creator_id': self.business_user.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_search_offers(self):
        self.client.force_authenticate(user=self.business_user)
        self.client.post(self.url, build_offer_payload(
            'Unique Title XYZ'), format='json')
        response = self.client.get(self.url, {'search': 'XYZ'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)


class OfferDetailUpdateDeleteTests(APITestCase):
    """Tests for GET/PATCH/DELETE /api/offers/{id}/"""

    def setUp(self):
        self.owner = User.objects.create_user(
            username='owner', password='pass123')
        UserProfile.objects.create(user=self.owner, type='business')
        self.other = User.objects.create_user(
            username='other', password='pass123')
        UserProfile.objects.create(user=self.other, type='business')
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(
            '/api/offers/', build_offer_payload(), format='json')
        self.offer_id = response.data['id']
        self.url = f'/api/offers/{self.offer_id}/'

    def test_get_offer_detail(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('min_price', response.data)

    def test_get_offer_not_found(self):
        response = self.client.get('/api/offers/9999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_offer_as_owner_success(self):
        response = self.client.patch(
            self.url, {'title': 'Updated Title'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_patch_offer_as_non_owner_forbidden(self):
        self.client.force_authenticate(user=self.other)
        response = self.client.patch(
            self.url, {'title': 'Hacked'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_offer_detail_by_offer_type(self):
        response = self.client.patch(
            self.url,
            {'details': [{'offer_type': 'basic', 'price': 150}]},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_detail = OfferDetail.objects.get(
            offer_id=self.offer_id, offer_type='basic')
        self.assertEqual(float(updated_detail.price), 150.0)

    def test_delete_offer_as_owner_success(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_offer_as_non_owner_forbidden(self):
        self.client.force_authenticate(user=self.other)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class OfferDetailRetrieveTests(APITestCase):
    """Tests for GET /api/offerdetails/{id}/"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='biz', password='pass123')
        UserProfile.objects.create(user=self.user, type='business')
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            '/api/offers/', build_offer_payload(), format='json')
        self.detail_id = response.data['details'][0]['id']

    def test_get_offerdetail_success(self):
        response = self.client.get(f'/api/offerdetails/{self.detail_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_offerdetail_not_found(self):
        response = self.client.get('/api/offerdetails/9999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
