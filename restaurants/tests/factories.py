import factory
from django.utils import timezone

from restaurants.models import Menu, MenuItem, Restaurant


class RestaurantFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Restaurant
        skip_postgeneration_save = True

    name = factory.Sequence(lambda n: f"Restaurant {n}")
    address = factory.Faker("address")
    contact_phone = factory.Faker("phone_number")
    contact_email = factory.Faker("email")


class MenuFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Menu
        skip_postgeneration_save = True

    restaurant = factory.SubFactory(RestaurantFactory)
    date = factory.LazyFunction(lambda: timezone.now().date())


class MenuItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MenuItem
        skip_postgeneration_save = True

    menu = factory.SubFactory(MenuFactory)
    name = factory.Sequence(lambda n: f"Dish {n}")
    description = factory.Faker("text", max_nb_chars=200)
    price = factory.Faker("pydecimal", left_digits=3, right_digits=2, positive=True)
