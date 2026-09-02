# Third-party
from rest_framework.pagination import PageNumberPagination


class OfferPagination(PageNumberPagination):
    """Pagination for GET /api/offers/ (the only list endpoint the frontend
    expects in {count, next, previous, results} form)."""

    page_size = 6
    page_size_query_param = 'page_size'
    max_page_size = 100
