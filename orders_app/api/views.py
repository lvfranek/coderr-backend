# Third-party
from django.db.models import Q
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

# Local imports
from profile_app.models import UserProfile
from ..models import Order
from .permissions import IsBusinessUserForOrder, IsCustomerUser, IsStaffUser
from .serializers import OrderCreateSerializer, OrderSerializer


class OrderListCreateView(generics.ListCreateAPIView):
    """GET orders involving the current user, POST creates a new one."""

    permission_classes = [permissions.IsAuthenticated, IsCustomerUser]

    def get_queryset(self):
        user = self.request.user
        return Order.objects.filter(
            Q(customer_user=user) | Q(business_user=user)
        )

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return OrderCreateSerializer
        return OrderSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        output = OrderSerializer(order)
        return Response(output.data, status=201)


class OrderUpdateDeleteView(generics.UpdateAPIView, generics.DestroyAPIView):
    """PATCH (business user only) and DELETE (staff only) a single order."""

    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [
        permissions.IsAuthenticated, IsBusinessUserForOrder, IsStaffUser,
    ]

    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [permissions.IsAuthenticated(), IsStaffUser()]
        return [permissions.IsAuthenticated(), IsBusinessUserForOrder()]


class OrderCountView(APIView):
    """GET /api/order-count/{business_user_id}/"""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, business_user_id):
        if not UserProfile.objects.filter(
            user_id=business_user_id, type=UserProfile.UserType.BUSINESS
        ).exists():
            return Response({'detail': 'Business user not found.'}, status=404)
        count = Order.objects.filter(
            business_user_id=business_user_id, status=Order.Status.IN_PROGRESS
        ).count()
        return Response({'order_count': count})


class CompletedOrderCountView(APIView):
    """GET /api/completed-order-count/{business_user_id}/"""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, business_user_id):
        if not UserProfile.objects.filter(
            user_id=business_user_id, type=UserProfile.UserType.BUSINESS
        ).exists():
            return Response({'detail': 'Business user not found.'}, status=404)
        count = Order.objects.filter(
            business_user_id=business_user_id, status=Order.Status.COMPLETED
        ).count()
        return Response({'completed_order_count': count})
