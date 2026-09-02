# Third-party
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, permissions

# Local imports
from ..models import Review
from .permissions import IsCustomerUser, IsReviewOwner
from .serializers import ReviewSerializer, ReviewUpdateSerializer


class ReviewListCreateView(generics.ListCreateAPIView):
    """GET all reviews (filterable/orderable), POST a new one (customers only)."""

    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated, IsCustomerUser]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['business_user', 'reviewer']
    ordering_fields = ['updated_at', 'rating']


class ReviewUpdateDeleteView(generics.UpdateAPIView, generics.DestroyAPIView):
    """PATCH/DELETE a review - only its creator may modify it."""

    queryset = Review.objects.all()
    serializer_class = ReviewUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, IsReviewOwner]
