from django.urls import path

from restaurants.views import (
    MenuCreateView,
    RestaurantDetailView,
    RestaurantListCreateView,
    TodayMenuListView,
)

app_name = "restaurants"

urlpatterns = [
    path("", RestaurantListCreateView.as_view(), name="restaurant-list"),
    path("<int:pk>/", RestaurantDetailView.as_view(), name="restaurant-detail"),
    path("<int:pk>/menu/", MenuCreateView.as_view(), name="menu-create"),
    path("menu/today/", TodayMenuListView.as_view(), name="today-menu-list"),
]
