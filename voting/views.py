from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import Count
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.response import Response

from voting.api.v1.serializers import (
    VoteDetailSerializerV1,
    VoteSerializerV1,
    VotingResultSerializerV1,
)
from voting.api.v2.serializers import (
    VoteDetailSerializerV2,
    VoteSerializerV2,
    VotingResultSerializerV2,
)
from voting.models import Vote


class VersionedSerializerMixin:
    """
    Mixin that selects the appropriate serializer based on the API version.
    """

    serializer_classes = {}
    default_version = "1.0"

    def get_serializer_class(self):
        version = getattr(self.request, "version", self.default_version)
        return self.serializer_classes.get(
            version, self.serializer_classes[self.default_version]
        )


class CreateVoteView(VersionedSerializerMixin, generics.CreateAPIView):
    serializer_classes = {
        "1.0": VoteSerializerV1,
        "2.0": VoteSerializerV2,
    }

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            vote = serializer.save()
            response_serializer = (
                VoteDetailSerializerV2(vote)
                if request.version == "2.0"
                else VoteDetailSerializerV1(vote)
            )
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        except (ValidationError, IntegrityError) as error:
            return Response({"detail": str(error)}, status=status.HTTP_400_BAD_REQUEST)


class UserVoteHistoryView(VersionedSerializerMixin, generics.ListAPIView):
    serializer_classes = {
        "1.0": VoteDetailSerializerV1,
        "2.0": VoteDetailSerializerV2,
    }

    def get_queryset(self):
        return Vote.objects.filter(employee=self.request.user).select_related(
            "menu", "menu__restaurant"
        )


class TodayResultsView(VersionedSerializerMixin, generics.ListAPIView):
    serializer_classes = {
        "1.0": VotingResultSerializerV1,
        "2.0": VotingResultSerializerV2,
    }

    def get_queryset(self):
        today = timezone.now().date()
        return (
            Vote.objects.filter(date=today)
            .select_related("menu", "menu__restaurant")
            .values("menu")
            .annotate(votes_count=Count("id"))
            .order_by("-votes_count")
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if self.request.version == "2.0":
            context["results"] = self.get_queryset()
        return context
