# Third-party
from django.urls import path

# Local imports
from .views import ReviewListCreateView, ReviewUpdateDeleteView

app_name = 'reviews_app'

urlpatterns = [
    path('reviews/', ReviewListCreateView.as_view(), name='review-list-create'),
    path('reviews/<int:pk>/', ReviewUpdateDeleteView.as_view(),
         name='review-update-delete'),
]
