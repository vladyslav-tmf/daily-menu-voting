import pytest
from django.contrib.auth import get_user_model

from authentication.tests.factories import EmployeeFactory

Employee = get_user_model()


@pytest.mark.django_db
class TestEmployeeModel:
    def test_create_employee(self):
        employee = EmployeeFactory()
        assert employee.pk is not None
        assert employee.is_active
        assert not employee.is_staff
        assert not employee.is_superuser
        assert employee.email
        assert employee.first_name
        assert employee.last_name
        assert employee.check_password("testpass123")

    def test_create_superuser(self):
        admin = EmployeeFactory(is_staff=True, is_superuser=True)
        assert admin.is_staff
        assert admin.is_superuser
        assert admin.is_active

    def test_employee_str(self):
        employee = EmployeeFactory(
            first_name="John", last_name="Doe", email="john@example.com"
        )
        expected_str = "John Doe (john@example.com)"
        assert str(employee) == expected_str

    def test_email_is_required(self):
        with pytest.raises(ValueError) as exc_info:
            Employee.objects.create_user(email="", password="testpass123")
        assert str(exc_info.value) == "The email field must be set"

    def test_create_superuser_with_invalid_flags(self):
        with pytest.raises(ValueError) as exc_info:
            Employee.objects.create_superuser(
                email="admin@example.com", password="testpass123", is_staff=False
            )
        assert str(exc_info.value) == "Superuser must have is_staff=True"

        with pytest.raises(ValueError) as exc_info:
            Employee.objects.create_superuser(
                email="admin@example.com", password="testpass123", is_superuser=False
            )
        assert str(exc_info.value) == "Superuser must have is_superuser=True"

    def test_normalize_email(self):
        email = "TEST@EXAMPLE.COM"
        employee = EmployeeFactory(email=email)
        assert employee.email == "TEST@example.com"
