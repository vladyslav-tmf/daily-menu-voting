import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from authentication.tests.factories import EmployeeFactory


@pytest.mark.django_db
class TestEmployeeRegistrationView:
    def setup_method(self):
        self.client = APIClient()
        self.url = reverse("authentication:register")

    def test_register_employee_success(self):
        data = {
            "email": "test@example.com",
            "password": "testpass123",
            "password_confirm": "testpass123",
            "first_name": "Test",
            "last_name": "User",
        }
        response = self.client.post(self.url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert "password" not in response.data
        assert response.data["email"] == data["email"]
        assert response.data["first_name"] == data["first_name"]
        assert response.data["last_name"] == data["last_name"]

    def test_register_employee_with_invalid_data(self):
        data = {
            "email": "invalid-email",
            "password": "short",
            "password_confirm": "short",
            "first_name": "",
            "last_name": "",
        }
        response = self.client.post(self.url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "email" in response.data
        assert "password" in response.data


@pytest.mark.django_db
class TestEmployeeProfileView:
    def setup_method(self):
        self.client = APIClient()
        self.url = reverse("authentication:profile")
        self.employee = EmployeeFactory()
        self.token = RefreshToken.for_user(self.employee).access_token
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

    def test_get_profile(self):
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["email"] == self.employee.email
        assert response.data["first_name"] == self.employee.first_name
        assert response.data["last_name"] == self.employee.last_name

    def test_update_profile(self):
        data = {
            "first_name": "Updated",
            "last_name": "Name",
        }
        response = self.client.patch(self.url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["first_name"] == data["first_name"]
        assert response.data["last_name"] == data["last_name"]

    def test_get_profile_unauthorized(self):
        self.client.credentials() # Remove authentication
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED



@pytest.mark.django_db
class TestTokenViews:
    def setup_method(self):
        self.client = APIClient()
        self.employee = EmployeeFactory()
        self.login_url = reverse("authentication:token-obtain-pair")
        self.refresh_url = reverse("authentication:token-refresh")
        self.verify_url = reverse("authentication:token-verify")

    def test_obtain_token_pair(self):
        data = {
            "email": self.employee.email,
            "password": "testpass123",
        }
        response = self.client.post(self.login_url, data)
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data

    def test_refresh_token(self):
        refresh = RefreshToken.for_user(self.employee)
        data = {"refresh": str(refresh)}
        response = self.client.post(self.refresh_url, data)
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data

    def test_verify_token(self):
        token = RefreshToken.for_user(self.employee).access_token
        data = {"token": str(token)}
        response = self.client.post(self.verify_url, data)
        assert response.status_code == status.HTTP_200_OK
