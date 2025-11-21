from django.urls import path
from auth_app.api.views import RegistrationView, LoginView, email_check

urlpatterns = [
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('login/', LoginView.as_view(), name='login'),
    path('email-check/', email_check, name='email-check'),
]