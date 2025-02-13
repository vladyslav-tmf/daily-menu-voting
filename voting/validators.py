from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_voting_time():
    now = timezone.localtime()
    if now.hour >= 11:
        raise ValidationError("Voting is only allowed before 11:00 AM")
