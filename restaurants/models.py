from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Restaurant(TimeStampedModel):
    name = models.CharField(max_length=255, unique=True, db_index=True)
    address = models.TextField()
    contact_phone = models.CharField(max_length=31)
    contact_email = models.EmailField()

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_menu_for_date(self, date=None):
        """
        Get menu for a specific date. If date is not provided, returns today's menu.
        """
        if not date:
            date = timezone.now().date()
        return self.menus.filter(date=date).first()


class Menu(TimeStampedModel):
    restaurant = models.ForeignKey(
        Restaurant, on_delete=models.CASCADE, related_name="menus"
    )
    date = models.DateField(default=timezone.now, db_index=True)

    class Meta:
        ordering = ["-date"]
        constraints = [
            models.UniqueConstraint(
                fields=["restaurant", "date"], name="unique_restaurant_daily_menu"
            )
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.date}"

    @property
    def is_today(self):
        return self.date == timezone.now().date()

    def clean(self):
        if (
            Menu.objects.filter(restaurant=self.restaurant, date=self.date)
            .exclude(pk=self.pk)
            .exists()
        ):
            raise ValidationError("Menu with this Restaurant and Date already exists")

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class MenuItem(TimeStampedModel):
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name="items")
    name = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0"))]
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} - {self.price}"

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
