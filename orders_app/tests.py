# Third-party
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

# Local imports
from offers_app.models import Offer, OfferDetail
from profile_app.models import UserProfile
from .models import Order


class OrderListCreateTests(APITestCase):
    """Tests for GET/POST /api/orders/"""

    def setUp(self):
        self.business_user = User.objects.create_user(
            username='biz', password='pass123')
        UserProfile.objects.create(user=self.business_user, type='business')
        self.customer_user = User.objects.create_user(
            username='cust', password='pass123')
        UserProfile.objects.create(user=self.customer_user, type='customer')
        offer = Offer.objects.create(user=self.business_user, title='Offer')
        self.detail = OfferDetail.objects.create(
            offer=offer, title='Basic', revisions=1, delivery_time_in_days=5,
            price=100, features=['A'], offer_type='basic',
        )
        self.url = '/api/orders/'

    def test_create_order_as_customer_success(self):
        self.client.force_authenticate(user=self.customer_user)
        response = self.client.post(
            self.url, {'offer_detail_id': self.detail.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['business_user'], self.business_user.id)

    def test_create_order_as_business_forbidden(self):
        self.client.force_authenticate(user=self.business_user)
        response = self.client.post(
            self.url, {'offer_detail_id': self.detail.id})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_order_invalid_detail_id(self):
        self.client.force_authenticate(user=self.customer_user)
        response = self.client.post(self.url, {'offer_detail_id': 9999})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_orders_requires_auth(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_orders_only_shows_involved_orders(self):
        self.client.force_authenticate(user=self.customer_user)
        self.client.post(self.url, {'offer_detail_id': self.detail.id})
        outsider = User.objects.create_user(
            username='outsider', password='pass123')
        UserProfile.objects.create(user=outsider, type='customer')
        self.client.force_authenticate(user=outsider)
        response = self.client.get(self.url)
        self.assertEqual(len(response.data), 0)


class OrderUpdateDeleteTests(APITestCase):
    """Tests for PATCH/DELETE /api/orders/{id}/"""

    def setUp(self):
        self.business_user = User.objects.create_user(
            username='biz', password='pass123')
        UserProfile.objects.create(user=self.business_user, type='business')
        self.customer_user = User.objects.create_user(
            username='cust', password='pass123')
        UserProfile.objects.create(user=self.customer_user, type='customer')
        self.admin = User.objects.create_superuser(
            username='admin', password='pass123', email='admin@mail.de'
        )
        self.order = Order.objects.create(
            customer_user=self.customer_user, business_user=self.business_user,
            title='Test', revisions=1, delivery_time_in_days=5, price=100,
            features=['A'], offer_type='basic',
        )
        self.url = f'/api/orders/{self.order.id}/'

    def test_patch_status_as_business_user_success(self):
        self.client.force_authenticate(user=self.business_user)
        response = self.client.patch(self.url, {'status': 'completed'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_patch_status_as_customer_forbidden(self):
        self.client.force_authenticate(user=self.customer_user)
        response = self.client.patch(self.url, {'status': 'completed'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_as_admin_success(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_as_non_admin_forbidden(self):
        self.client.force_authenticate(user=self.business_user)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class OrderCountTests(APITestCase):
    """Tests for /api/order-count/ and /api/completed-order-count/"""

    def setUp(self):
        self.business_user = User.objects.create_user(
            username='biz', password='pass123')
        UserProfile.objects.create(user=self.business_user, type='business')
        self.customer_user = User.objects.create_user(
            username='cust', password='pass123')
        UserProfile.objects.create(user=self.customer_user, type='customer')
        Order.objects.create(
            customer_user=self.customer_user, business_user=self.business_user,
            title='A', revisions=1, delivery_time_in_days=5, price=100,
            features=[], offer_type='basic', status='in_progress',
        )
        Order.objects.create(
            customer_user=self.customer_user, business_user=self.business_user,
            title='B', revisions=1, delivery_time_in_days=5, price=100,
            features=[], offer_type='basic', status='completed',
        )
        self.client.force_authenticate(user=self.customer_user)

    def test_order_count_success(self):
        response = self.client.get(
            f'/api/order-count/{self.business_user.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['order_count'], 1)

    def test_order_count_unknown_business_user(self):
        response = self.client.get('/api/order-count/9999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_completed_order_count_success(self):
        response = self.client.get(
            f'/api/completed-order-count/{self.business_user.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['completed_order_count'], 1)
