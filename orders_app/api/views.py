from django.db.models import Q
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from profile_app.models import UserProfile
from ..models import Order
from .permissions import IsBusinessUserForOrder, IsCustomerUser, IsStaffUser
from .serializers import OrderCreateSerializer, OrderSerializer


def business_status_count(business_user_id, status_value, key):
    """404 unless the id is a real business user, otherwise the status count."""
    if not UserProfile.objects.filter(
        user_id=business_user_id, type=UserProfile.UserType.BUSINESS
    ).exists():
        return Response(
            {'detail': 'Business user not found.'},
            status=status.HTTP_404_NOT_FOUND,
        )
    count = Order.objects.filter(
        business_user_id=business_user_id, status=status_value
    ).count()
    return Response({key: count})


class OrderListCreateView(generics.ListCreateAPIView):
    """GET orders involving the current user, POST creates a new one."""

    permission_classes = [permissions.IsAuthenticated, IsCustomerUser]

    def get_queryset(self):
        """Show only orders where the user is buyer or seller."""
        user = self.request.user
        return Order.objects.filter(
            Q(customer_user=user) | Q(business_user=user)
        )

    def get_serializer_class(self):
        """Slim input serializer for POST, full serializer otherwise."""
        if self.request.method == 'POST':
            return OrderCreateSerializer
        return OrderSerializer

    def create(self, request, *args, **kwargs):
        """Create from an offer_detail_id, then respond with the full order."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        output = OrderSerializer(order)
        return Response(output.data, status=status.HTTP_201_CREATED)


class OrderUpdateDeleteView(generics.UpdateAPIView, generics.DestroyAPIView):
    """PATCH (business user only) and DELETE (staff only) a single order."""

    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [
        permissions.IsAuthenticated, IsBusinessUserForOrder, IsStaffUser,
    ]

    def get_permissions(self):
        """DELETE is staff-only; PATCH is limited to the order's business user."""
        if self.request.method == 'DELETE':
            return [permissions.IsAuthenticated(), IsStaffUser()]
        return [permissions.IsAuthenticated(), IsBusinessUserForOrder()]


class OrderCountView(APIView):
    """GET /api/order-count/{business_user_id}/ - open orders of a business."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, business_user_id):
        return business_status_count(
            business_user_id, Order.Status.IN_PROGRESS, 'order_count')


class CompletedOrderCountView(APIView):
    """GET /api/completed-order-count/{business_user_id}/ - completed orders."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, business_user_id):
        return business_status_count(
            business_user_id, Order.Status.COMPLETED, 'completed_order_count')
