from django.urls import path

from .views import BaseInfoView

app_name = 'base_info_app'

urlpatterns = [
    path('base-info/', BaseInfoView.as_view(), name='base-info'),
]
