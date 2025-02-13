from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import Count
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.response import Response

from voting.models import Vote
from voting.serializers import (
    VoteDetailSerializer,
    VoteSerializer,
    VotingResultSerializer,
)


class CreateVoteView(generics.CreateAPIView):
    serializer_class = VoteSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            vote = serializer.save()
            response_serializer = VoteDetailSerializer(vote)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        except (ValidationError, IntegrityError) as error:
            return Response({"detail": str(error)}, status=status.HTTP_400_BAD_REQUEST)


class UserVoteHistoryView(generics.ListAPIView):
    serializer_class = VoteDetailSerializer

    def get_queryset(self):
        return Vote.objects.filter(employee=self.request.user).select_related(
            "menu", "menu__restaurant"
        )


class TodayResultsView(generics.ListAPIView):
    serializer_class = VotingResultSerializer

    def get_queryset(self):
        today = timezone.now().date()
        return (
            Vote.objects.filter(date=today)
            .select_related("menu", "menu__restaurant")
            .values("menu")
            .annotate(votes_count=Count("id"))
            .order_by("-votes_count")
        )
