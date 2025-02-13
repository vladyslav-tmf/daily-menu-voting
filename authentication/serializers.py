from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

Employee = get_user_model()


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ("id", "email", "first_name", "last_name", "date_joined", "is_active")
        read_only_fields = ("id", "date_joined", "is_active")


class EmployeeRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
        style={"input_type": "password"},
    )
    password_confirm = serializers.CharField(
        write_only=True, style={"input_type": "password"}
    )

    class Meta:
        model = Employee
        fields = ("email", "password", "password_confirm", "first_name", "last_name")

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {"password_confirm": "Passwords do not match"}
            )
        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        return Employee.objects.create_user(**validated_data)
