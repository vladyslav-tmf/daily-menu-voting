from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from authentication.views import EmployeeProfileView, EmployeeRegistrationView

app_name = "authentication"

urlpatterns = [
    path("register/", EmployeeRegistrationView.as_view(), name="register"),
    path("profile/", EmployeeProfileView.as_view(), name="profile"),
    path("token/", TokenObtainPairView.as_view(), name="token-obtain-pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token-verify"),
]
