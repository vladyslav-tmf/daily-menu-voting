from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from restaurants.models import Menu
from voting.validators import validate_voting_time


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Vote(TimeStampedModel):
    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="votes"
    )
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name="votes")
    date = models.DateField(default=timezone.now)

    class Meta:
        ordering = ["-date"]
        constraints = [
            models.UniqueConstraint(
                fields=["employee", "date"], name="one_vote_per_day"
            )
        ]

    def __str__(self):
        return f"{self.employee} voted for {self.menu} on {self.date}"

    def clean(self):
        """
        Validate that:
        1. Vote is for today's menu
        2. Voting is before 11:00 AM
        """
        if self.date != timezone.now().date():
            raise ValidationError("You can only vote for today's menu")
        validate_voting_time()

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
