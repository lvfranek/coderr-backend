from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, permissions

from ..models import Offer, OfferDetail
from .filter import OfferIntFilterMixin
from .pagination import OfferPagination
from .permissions import IsBusinessUser, IsOfferOwner
from .serializers import (
    OfferCreateUpdateSerializer,
    OfferDetailSerializer,
    OfferSerializer,
)


class OfferListCreateView(OfferIntFilterMixin, generics.ListCreateAPIView):
    """GET (public, filterable/paginated) and POST (business users only)."""

    queryset = Offer.objects.all()
    pagination_class = OfferPagination
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly, IsBusinessUser]
    filter_backends = [DjangoFilterBackend,
                       filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['user']
    ordering_fields = ['updated_at']
    search_fields = ['title', 'description']

    def get_serializer_class(self):
        """Use the write serializer for POST, the read serializer otherwise."""
        if self.request.method == 'POST':
            return OfferCreateUpdateSerializer
        return OfferSerializer


class OfferDetailUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    """GET (any authenticated user), PATCH/DELETE (only the owner)."""

    queryset = Offer.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsOfferOwner]

    def get_serializer_class(self):
        """Write serializer for PATCH/PUT, read serializer for GET."""
        if self.request.method in ('PATCH', 'PUT'):
            return OfferCreateUpdateSerializer
        return OfferSerializer


class OfferDetailRetrieveView(generics.RetrieveAPIView):
    """GET /api/offerdetails/{id}/ - a single pricing tier."""

    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
