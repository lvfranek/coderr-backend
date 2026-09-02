# Third-party
from django.urls import path

# Local imports
from .views import (
    CompletedOrderCountView,
    OrderCountView,
    OrderListCreateView,
    OrderUpdateDeleteView,
)

app_name = 'orders_app'

urlpatterns = [
    path('orders/', OrderListCreateView.as_view(), name='order-list-create'),
    path('orders/<int:pk>/', OrderUpdateDeleteView.as_view(),
         name='order-update-delete'),
    path('order-count/<int:business_user_id>/',
         OrderCountView.as_view(), name='order-count'),
    path(
        'completed-order-count/<int:business_user_id>/',
        CompletedOrderCountView.as_view(),
        name='completed-order-count',
    ),
]
