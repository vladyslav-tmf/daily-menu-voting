from decimal import Decimal

import pytest
from django.utils import timezone

from restaurants.serializers import (
    MenuDetailSerializer,
    MenuItemSerializer,
    MenuSerializer,
    RestaurantDetailSerializer,
    RestaurantSerializer,
)
from restaurants.tests.factories import MenuFactory, MenuItemFactory, RestaurantFactory


@pytest.mark.django_db
class TestMenuItemSerializer:
    def test_serialize_menu_item(self):
        menu_item = MenuItemFactory()
        serializer = MenuItemSerializer(menu_item)

        assert serializer.data["id"] == menu_item.id
        assert serializer.data["name"] == menu_item.name
        assert serializer.data["description"] == menu_item.description
        assert Decimal(serializer.data["price"]) == menu_item.price

    def test_deserialize_valid_data(self):
        valid_data = {
            "name": "Test Item",
            "description": "Test Description",
            "price": "10.99",
        }
        serializer = MenuItemSerializer(data=valid_data)
        assert serializer.is_valid()
        assert serializer.validated_data["name"] == valid_data["name"]
        assert serializer.validated_data["description"] == valid_data["description"]
        assert Decimal(serializer.validated_data["price"]) == Decimal(
            valid_data["price"]
        )

    def test_deserialize_invalid_price(self):
        invalid_data = {
            "name": "Test Item",
            "description": "Test Description",
            "price": "-10.99",
        }
        serializer = MenuItemSerializer(data=invalid_data)
        assert not serializer.is_valid()
        assert "price" in serializer.errors


@pytest.mark.django_db
class TestMenuSerializer:
    def test_serialize_menu_with_items(self):
        menu = MenuFactory()
        menu_items = [MenuItemFactory(menu=menu) for _ in range(3)]
        serializer = MenuSerializer(menu)

        assert serializer.data["id"] == menu.id
        assert serializer.data["restaurant"] == menu.restaurant_id
        assert serializer.data["date"] == menu.date.isoformat()
        assert len(serializer.data["items"]) == len(menu_items)

    def test_create_menu_with_items(self):
        restaurant = RestaurantFactory()
        menu_data = {
            "restaurant": restaurant.id,
            "date": timezone.now().date().isoformat(),
            "items": [
                {
                    "name": "Item 1",
                    "description": "Description 1",
                    "price": "10.99",
                },
                {
                    "name": "Item 2",
                    "description": "Description 2",
                    "price": "15.99",
                },
            ],
        }
        serializer = MenuSerializer(data=menu_data)
        assert serializer.is_valid()

        menu = serializer.save(restaurant=restaurant)
        assert menu.restaurant == restaurant
        assert menu.items.count() == 2

    def test_restaurant_is_read_only(self):
        menu = MenuFactory()
        new_restaurant = RestaurantFactory()
        serializer = MenuSerializer(
            menu, data={"restaurant": new_restaurant.id, "date": menu.date}
        )
        assert serializer.is_valid()
        updated_menu = serializer.save()
        assert updated_menu.restaurant == menu.restaurant


@pytest.mark.django_db
class TestMenuDetailSerializer:
    def test_serialize_menu_with_restaurant_name(self):
        menu = MenuFactory()
        MenuItemFactory(menu=menu)
        serializer = MenuDetailSerializer(menu)

        assert serializer.data["id"] == menu.id
        assert serializer.data["restaurant"] == str(menu.restaurant)
        assert serializer.data["date"] == menu.date.isoformat()
        assert len(serializer.data["items"]) == 1


@pytest.mark.django_db
class TestRestaurantSerializer:
    def test_serialize_restaurant(self):
        restaurant = RestaurantFactory()
        serializer = RestaurantSerializer(restaurant)

        assert serializer.data["id"] == restaurant.id
        assert serializer.data["name"] == restaurant.name
        assert serializer.data["address"] == restaurant.address
        assert serializer.data["contact_phone"] == restaurant.contact_phone
        assert serializer.data["contact_email"] == restaurant.contact_email
        assert "created_at" in serializer.data
        assert "updated_at" in serializer.data

    def test_create_restaurant(self):
        data = {
            "name": "Test Restaurant",
            "address": "Test Address",
            "contact_phone": "1234567890",
            "contact_email": "test@example.com",
        }
        serializer = RestaurantSerializer(data=data)
        assert serializer.is_valid()
        restaurant = serializer.save()

        assert restaurant.name == data["name"]
        assert restaurant.address == data["address"]
        assert restaurant.contact_phone == data["contact_phone"]
        assert restaurant.contact_email == data["contact_email"]

    def test_validate_duplicate_name(self):
        existing_restaurant = RestaurantFactory()
        data = {
            "name": existing_restaurant.name,
            "address": "New Address",
            "contact_phone": "1234567890",
            "contact_email": "new@example.com",
        }
        serializer = RestaurantSerializer(data=data)
        assert not serializer.is_valid()
        assert "name" in serializer.errors


@pytest.mark.django_db
class TestRestaurantDetailSerializer:
    def test_serialize_with_today_menu(self):
        restaurant = RestaurantFactory()
        menu = MenuFactory(restaurant=restaurant, date=timezone.now().date())
        MenuItemFactory(menu=menu)

        serializer = RestaurantDetailSerializer(restaurant)
        assert serializer.data["id"] == restaurant.id
        assert serializer.data["today_menu"] is not None
        assert serializer.data["today_menu"]["id"] == menu.id
        assert len(serializer.data["today_menu"]["items"]) == 1

    def test_serialize_without_today_menu(self):
        restaurant = RestaurantFactory()
        MenuFactory(
            restaurant=restaurant,
            date=timezone.now().date() + timezone.timedelta(days=1),
        )

        serializer = RestaurantDetailSerializer(restaurant)
        assert serializer.data["id"] == restaurant.id
        assert serializer.data["today_menu"] is None
