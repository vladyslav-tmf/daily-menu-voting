from http.client import responses

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from authentication.tests.factories import EmployeeFactory
from restaurants.tests.factories import MenuFactory, MenuItemFactory, RestaurantFactory


@pytest.mark.django_db
class TestRestaurantListCreateView:
    def setup_method(self):
        self.client = APIClient()
        self.url = reverse("restaurants:restaurant-list")
        self.user = EmployeeFactory()
        self.admin = EmployeeFactory(is_staff=True)

    def test_list_restaurants(self):
        restaurants = [RestaurantFactory() for _ in range(3)]
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == len(restaurants)

    def test_create_restaurant_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        data = {
            "name": "New Restaurant",
            "address": "Test Address",
            "contact_phone": "1234567890",
            "contact_email": "test@example.com",
        }
        response = self.client.post(self.url, data)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == data["name"]

    def test_create_restaurant_as_regular_user(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "name": "New Restaurant",
            "address": "Test Address",
            "contact_phone": "1234567890",
            "contact_email": "test@example.com",
        }
        response = self.client.post(self.url, data)

        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestRestaurantDetailView:
    def setup_method(self):
        self.client = APIClient()
        self.restaurant = RestaurantFactory()
        self.url = reverse(
            "restaurants:restaurant-detail", kwargs={"pk": self.restaurant.pk}
        )
        self.user = EmployeeFactory()
        self.admin = EmployeeFactory(is_staff=True)

    def test_retrieve_restaurant(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == self.restaurant.id
        assert response.data["name"] == self.restaurant.name

    def test_update_restaurant_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        data = {"name": "Updated Restaurant"}
        response = self.client.patch(self.url, data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == data["name"]

    def test_update_restaurant_as_regular_user(self):
        self.client.force_authenticate(user=self.user)
        data = {"name": "Updated Restaurant"}
        response = self.client.patch(self.url, data)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_restaurant_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(self.url)

        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_delete_restaurant_as_regular_user(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.url)

        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestMenuCreateView:
    def setup_method(self):
        self.client = APIClient()
        self.restaurant = RestaurantFactory()
        self.url = reverse("restaurants:menu-create", kwargs={"pk": self.restaurant.pk})
        self.user = EmployeeFactory()
        self.admin = EmployeeFactory(is_staff=True)

    def test_create_menu_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        data = {
            "date": timezone.now().date().isoformat(),
            "items": [
                {
                    "name": "Test Item",
                    "description": "Test Description",
                    "price": "10.99",
                }
            ],
        }
        response = self.client.post(self.url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["restaurant"] == self.restaurant.id
        assert len(response.data["items"]) == 1

    def test_create_duplicate_menu(self):
        menu = MenuFactory(restaurant=self.restaurant, date=timezone.now().date())
        self.client.force_authenticate(user=self.admin)
        data = {
            "date": menu.date.isoformat(),
            "items": [
                {
                    "name": "Test Item",
                    "description": "Test Description",
                    "price": "10.99",
                }
            ],
        }
        response = self.client.post(self.url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "detail" in response.data

    def test_create_menu_as_regular_user(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "date": timezone.now().date().isoformat(),
            "items": [
                {
                    "name": "Test Item",
                    "description": "Test Description",
                    "price": "10.99",
                }
            ],
        }
        response = self.client.post(self.url, data, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestTodayMenuListView:
    def setup_method(self):
        self.client = APIClient()
        self.url = reverse("restaurants:today-menu-list")
        self.user = EmployeeFactory()
        self.client.force_authenticate(user=self.user)

    def test_list_today_menus(self):
        today_menus = [MenuFactory(date=timezone.now().date()) for _ in range(2)]
        for menu in today_menus:
            MenuItemFactory(menu=menu)

        tomorrow = timezone.now().date() + timezone.timedelta(days=1)
        tomorrow_menu = MenuFactory(date=tomorrow)
        MenuItemFactory(menu=tomorrow_menu)

        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == len(today_menus)
        for menu_data in response.data["results"]:
            assert menu_data["date"] == timezone.now().date().isoformat()

    def test_list_today_menus_when_empty(self):
        tomorrow = timezone.now().date() + timezone.timedelta(days=1)
        tomorrow_menu = MenuFactory(date=tomorrow)
        MenuItemFactory(menu=tomorrow_menu)

        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 0
