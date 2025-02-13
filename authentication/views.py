from rest_framework import generics, permissions, status
from rest_framework.response import Response

from authentication.serializers import (
    EmployeeRegistrationSerializer,
    EmployeeSerializer,
)


class EmployeeRegistrationView(generics.CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = EmployeeRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        # Create a response with user data (excluding password)
        response_serializer = EmployeeSerializer(instance=serializer.instance)
        return Response(
            response_serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )


class EmployeeProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = EmployeeSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user
