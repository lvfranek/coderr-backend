# Third-party
from django.urls import path

# Local imports
from .views import LoginView, RegistrationView

app_name = 'auth_app'

urlpatterns = [
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('login/', LoginView.as_view(), name='login'),
]
