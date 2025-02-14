import factory
from django.utils import timezone

from authentication.tests.factories import EmployeeFactory
from restaurants.tests.factories import MenuFactory
from voting.models import Vote


class VoteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Vote
        skip_postgeneration_save = True

    employee = factory.SubFactory(EmployeeFactory)
    menu = factory.SubFactory(MenuFactory)
    date = factory.LazyFunction(lambda: timezone.now().date())
