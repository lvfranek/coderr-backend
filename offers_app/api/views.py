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

    # Maps a query param to the ORM lookup it drives.
    INT_FILTERS = {
        'creator_id': 'user_id',
        'min_price': 'details__price__gte',
        'max_delivery_time': 'details__delivery_time_in_days__lte',
    }

    def get_serializer_class(self):
        # Use the write serializer for POST, the read serializer otherwise.
        if self.request.method == 'POST':
            return OfferCreateUpdateSerializer
        return OfferSerializer

    def get_queryset(self):
        # Apply each optional integer filter that was actually supplied.
        queryset = super().get_queryset()
        for param, lookup in self.INT_FILTERS.items():
            value = self._int_param(param)
            if value is not None:
                queryset = queryset.filter(**{lookup: value}).distinct()
        return queryset

    def _int_param(self, name):
        """Return the query param as an int, or None if it wasn't given.

        Raises a 400 (instead of a 500) when the value isn't a valid integer.
        """
        raw = self.request.query_params.get(name)
        # Treat a missing or empty param as "no filter".
        if raw in (None, ''):
            return None
        # Reject anything that isn't a plain integer with a 400.
        try:
            return int(raw)
        except (TypeError, ValueError):
            raise ValidationError({name: 'A valid integer is required.'})


class OfferDetailUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    """GET (any authenticated user), PATCH/DELETE (only the owner)."""

    queryset = Offer.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsOfferOwner]

    def get_serializer_class(self):
        # Write serializer for PATCH/PUT, read serializer for GET.
        if self.request.method in ('PATCH', 'PUT'):
            return OfferCreateUpdateSerializer
        return OfferSerializer


class OfferDetailRetrieveView(generics.RetrieveAPIView):
    """GET /api/offerdetails/{id}/ - a single pricing tier."""

    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
