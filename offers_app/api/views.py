# Third-party
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, permissions
from rest_framework.exceptions import ValidationError

# Local imports
from ..models import Offer, OfferDetail
from .pagination import OfferPagination
from .permissions import IsBusinessUser, IsOfferOwner
from .serializers import (
    OfferCreateUpdateSerializer,
    OfferDetailSerializer,
    OfferSerializer,
)


class OfferListCreateView(generics.ListCreateAPIView):
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
        if self.request.method == 'POST':
            return OfferCreateUpdateSerializer
        return OfferSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        creator_id = self._int_param('creator_id')
        min_price = self._int_param('min_price')
        max_delivery_time = self._int_param('max_delivery_time')
        if creator_id is not None:
            queryset = queryset.filter(user_id=creator_id)
        if min_price is not None:
            queryset = queryset.filter(
                details__price__gte=min_price).distinct()
        if max_delivery_time is not None:
            queryset = queryset.filter(
                details__delivery_time_in_days__lte=max_delivery_time
            ).distinct()
        return queryset

    def _int_param(self, name):
        """Return the query param as an int, or None if it wasn't given.

        Raises a 400 (instead of a 500) when the value isn't a valid integer.
        """
        raw = self.request.query_params.get(name)
        if raw in (None, ''):
            return None
        try:
            return int(raw)
        except (TypeError, ValueError):
            raise ValidationError({name: 'A valid integer is required.'})


class OfferDetailUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    """GET (any authenticated user), PATCH/DELETE (only the owner)."""

    queryset = Offer.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsOfferOwner]

    def get_serializer_class(self):
        if self.request.method in ('PATCH', 'PUT'):
            return OfferCreateUpdateSerializer
        return OfferSerializer


class OfferDetailRetrieveView(generics.RetrieveAPIView):
    """GET /api/offerdetails/{id}/ - a single pricing tier."""

    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
