# Third-party
from django.urls import path

# Local imports
from .views import BaseInfoView

app_name = 'base_info_app'

urlpatterns = [
    path('base-info/', BaseInfoView.as_view(), name='base-info'),
]
