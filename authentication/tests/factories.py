import factory
from django.contrib.auth import get_user_model

Employee = get_user_model()


class EmployeeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Employee
        skip_postgeneration_save = True

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    is_active = True
    _password = "testpass123"

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        if "password" in kwargs:
            cls._password = kwargs.pop("password")

        if kwargs.get("is_superuser"):
            obj = super()._create(model_class, *args, **kwargs)
            obj.set_password(cls._password)
            obj.save()
            return obj

        manager = cls._get_manager(model_class)
        return manager.create_user(*args, password=cls._password, **kwargs)

    @factory.post_generation
    def groups(self, create, extracted, **kwargs):
        if not create or not extracted:
            return

        self.groups.add(*extracted)
        self.save()

    @factory.post_generation
    def user_permissions(self, create, extracted, **kwargs):
        if not create or not extracted:
            return

        self.user_permissions.add(*extracted)
        self.save()
