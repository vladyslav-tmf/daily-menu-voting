from django.utils import timezone
from rest_framework import generics
from rest_framework.exceptions import ValidationError

from restaurants.models import Menu, Restaurant
from restaurants.permissions import IsAdminOrReadOnly
from restaurants.serializers import (
    MenuDetailSerializer,
    MenuSerializer,
    RestaurantDetailSerializer,
    RestaurantSerializer,
)


class RestaurantListCreateView(generics.ListCreateAPIView):
    queryset = Restaurant.objects.all()
    permission_classes = (IsAdminOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return RestaurantSerializer
        return RestaurantDetailSerializer


class RestaurantDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantDetailSerializer
    permission_classes = (IsAdminOrReadOnly,)


class MenuCreateView(generics.CreateAPIView):
    serializer_class = MenuSerializer
    permission_classes = (IsAdminOrReadOnly,)

    def perform_create(self, serializer):
        restaurant = generics.get_object_or_404(Restaurant, pk=self.kwargs["pk"])
        date = serializer.validated_data.get("date", timezone.now().date())
        if Menu.objects.filter(restaurant=restaurant, date=date).exists():
            raise ValidationError({"detail": "Menu for this date already exists"})
        serializer.save(restaurant=restaurant)


class TodayMenuListView(generics.ListAPIView):
    serializer_class = MenuDetailSerializer

    def get_queryset(self):
        today = timezone.now().date()
        return Menu.objects.filter(date=today).select_related("restaurant")
