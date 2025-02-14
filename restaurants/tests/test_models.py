import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from restaurants.tests.factories import MenuFactory, MenuItemFactory, RestaurantFactory


@pytest.mark.django_db
class TestRestaurantModel:
    def test_create_restaurant(self):
        restaurant = RestaurantFactory()
        assert restaurant.pk is not None
        assert restaurant.name
        assert restaurant.address
        assert restaurant.contact_phone
        assert restaurant.contact_email

    def test_restaurant_str(self):
        restaurant = RestaurantFactory(name="Test Restaurant")
        assert str(restaurant) == "Test Restaurant"

    def test_get_menu_for_date(self):
        restaurant = RestaurantFactory()
        menu = MenuFactory(restaurant=restaurant)

        assert restaurant.get_menu_for_date() == menu
        assert restaurant.get_menu_for_date(menu.date) == menu

        future_date = timezone.now().date() + timezone.timedelta(days=7)
        assert not restaurant.get_menu_for_date(future_date)


@pytest.mark.django_db
class TestMenuModel:
    def test_create_menu(self):
        menu = MenuFactory()
        assert menu.pk is not None
        assert menu.restaurant
        assert menu.date

    def test_menu_str(self):
        restaurant = RestaurantFactory(name="Test Restaurant")
        menu = MenuFactory(
            restaurant=restaurant, date=timezone.datetime(2025, 2, 13).date()
        )
        assert str(menu) == "Test Restaurant - 2025-02-13"

    def test_unique_restaurant_daily_menu(self):
        menu = MenuFactory()
        duplicate_menu = MenuFactory.build(restaurant=menu.restaurant, date=menu.date)

        with pytest.raises(ValidationError) as exc_info:
            duplicate_menu.full_clean()
        assert "Menu with this Restaurant and Date already exists" in str(
            exc_info.value
        )

    def test_is_today_property(self):
        today_menu = MenuFactory(date=timezone.now().date())
        assert today_menu.is_today

        tomorrow = timezone.now().date() + timezone.timedelta(days=1)
        tomorrow_menu = MenuFactory(date=tomorrow)
        assert not tomorrow_menu.is_today


@pytest.mark.django_db
class TestMenuItemModel:
    def test_create_menu_item(self):
        menu_item = MenuItemFactory()
        assert menu_item.pk is not None
        assert menu_item.menu
        assert menu_item.name
        assert menu_item.price > 0

    def test_menu_item_str(self):
        menu_item = MenuItemFactory(name="Test Dish", price="10.99")
        assert str(menu_item) == "Test Dish - 10.99"

    def test_price_validation(self):
        menu_item = MenuItemFactory.build(price=-10.99)
        with pytest.raises(ValidationError) as exc_info:
            menu_item.full_clean()
        assert "Ensure this value is greater than or equal to 0" in str(exc_info)
