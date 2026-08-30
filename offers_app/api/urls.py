# Third-party
from django.urls import path

# Local imports
from .views import (
    OfferDetailRetrieveView,
    OfferDetailUpdateDeleteView,
    OfferListCreateView,
)

app_name = 'offers_app'

urlpatterns = [
    path('offers/', OfferListCreateView.as_view(), name='offer-list-create'),
    path('offers/<int:pk>/', OfferDetailUpdateDeleteView.as_view(),
         name='offer-detail'),
    path('offerdetails/<int:pk>/', OfferDetailRetrieveView.as_view(),
         name='offerdetail-detail'),
]
