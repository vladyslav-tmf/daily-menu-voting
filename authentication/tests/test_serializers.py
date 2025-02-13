import pytest
from django.contrib.auth import get_user_model

from authentication.serializers import (
    EmployeeRegistrationSerializer,
    EmployeeSerializer,
)
from authentication.tests.factories import EmployeeFactory

Employee = get_user_model()


@pytest.mark.django_db
class TestEmployeeSerializer:
    def test_serialize_employee(self):
        employee = EmployeeFactory()
        serializer = EmployeeSerializer(employee)

        assert serializer.data["email"] == employee.email
        assert serializer.data["first_name"] == employee.first_name
        assert serializer.data["last_name"] == employee.last_name
        assert "password" not in serializer.data

    def test_serialize_employee_with_read_only_fields(self):
        employee = EmployeeFactory()
        serializer = EmployeeSerializer(employee)

        assert "id" in serializer.data
        assert "date_joined" in serializer.data
        assert "is_active" in serializer.data


@pytest.mark.django_db
class TestEmployeeRegistrationSerializer:
    def test_validate_passwords_dont_match(self):
        data = {
            "email": "test@example.com",
            "password": "testpass123",
            "password_confirm": "wrongpass",
            "first_name": "Test",
            "last_name": "User",
        }
        serializer = EmployeeRegistrationSerializer(data=data)
        assert not serializer.is_valid()
        assert "password_confirm" in serializer.errors

    def test_create_employee(self):
        data = {
            "email": "test@example.com",
            "password": "testpass123",
            "password_confirm": "testpass123",
            "first_name": "Test",
            "last_name": "User",
        }
        serializer = EmployeeRegistrationSerializer(data=data)
        assert serializer.is_valid()

        employee = serializer.save()
        assert employee.email == data["email"]
        assert employee.first_name == data["first_name"]
        assert employee.last_name == data["last_name"]
        assert employee.check_password(data["password"])
        assert not employee.is_staff
        assert not employee.is_superuser
