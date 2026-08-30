# Third-party
from django.urls import path

# Local imports
from .views import (
    BusinessProfileListView,
    CustomerProfileListView,
    ProfileDetailView,
)

app_name = 'profile_app'

urlpatterns = [
    path('profile/<int:pk>/', ProfileDetailView.as_view(), name='profile-detail'),
    path('profiles/business/', BusinessProfileListView.as_view(),
         name='business-list'),
    path('profiles/customer/', CustomerProfileListView.as_view(),
         name='customer-list'),
]
