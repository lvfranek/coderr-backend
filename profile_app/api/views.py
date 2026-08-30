# Third-party
from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied

# Local imports
from ..models import UserProfile
from .permissions import IsProfileOwner
from .serializers import (
    BusinessProfileListSerializer,
    CustomerProfileListSerializer,
    UserProfileSerializer,
)


class ProfileDetailView(generics.RetrieveUpdateAPIView):
    """GET/PATCH a single user's profile, addressed by user id (pk)."""

    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    lookup_field = 'user_id'
    lookup_url_kwarg = 'pk'
    permission_classes = [permissions.IsAuthenticated, IsProfileOwner]

    def perform_update(self, serializer):
        if serializer.instance.user != self.request.user:
            raise PermissionDenied("You can only edit your own profile.")
        serializer.save()


class BusinessProfileListView(generics.ListAPIView):
    """GET /api/profiles/business/ - lists all business profiles."""

    queryset = UserProfile.objects.filter(type=UserProfile.UserType.BUSINESS)
    serializer_class = BusinessProfileListSerializer
    permission_classes = [permissions.IsAuthenticated]


class CustomerProfileListView(generics.ListAPIView):
    """GET /api/profiles/customer/ - lists all customer profiles."""

    queryset = UserProfile.objects.filter(type=UserProfile.UserType.CUSTOMER)
    serializer_class = CustomerProfileListSerializer
    permission_classes = [permissions.IsAuthenticated]
