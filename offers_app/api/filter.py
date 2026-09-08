from rest_framework.exceptions import ValidationError


class OfferIntFilterMixin:
    """Applies the optional integer query-param filters for offer lists.

    Kept separate from the view so the parsing rules (and the 400-instead-of-500
    behaviour for non-numeric values) live in one place. INT_FILTERS maps each
    query param to the ORM lookup it drives.
    """

    INT_FILTERS = {
        'creator_id': 'user_id',
        'min_price': 'details__price__gte',
        'max_delivery_time': 'details__delivery_time_in_days__lte',
    }

    def get_queryset(self):
        """Apply each optional integer filter that was actually supplied."""
        queryset = super().get_queryset()
        for param, lookup in self.INT_FILTERS.items():
            value = self._int_param(param)
            if value is not None:
                queryset = queryset.filter(**{lookup: value}).distinct()
        return queryset

    """Treat a missing or empty param as no filter."""
    """Reject anything that isn't a plain integer with a 400."""
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
