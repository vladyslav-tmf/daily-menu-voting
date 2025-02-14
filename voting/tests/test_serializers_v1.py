from datetime import datetime, time
from unittest.mock import patch

import pytest
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from restaurants.tests.factories import MenuFactory
from voting.api.v1.serializers import (
    VoteDetailSerializerV1,
    VoteSerializerV1,
    VotingResultSerializerV1,
)
from voting.tests.factories import VoteFactory


@pytest.mark.django_db
class TestVoteSerializerV1:
    def setup_method(self):
        self.patcher = patch("django.utils.timezone.localtime")
        self.mock_localtime = self.patcher.start()
        mock_time = datetime.combine(timezone.now().date(), time(10, 0))
        self.mock_localtime.return_value = mock_time

    def teardown_method(self):
        self.patcher.stop()

    def test_serialize_vote(self):
        vote = VoteFactory()
        serializer = VoteSerializerV1(vote)

        assert serializer.data["id"] == vote.id
        assert serializer.data["menu"] == vote.menu.id
        assert serializer.data["date"] == vote.date.isoformat()

    def test_validate_menu_today(self):
        menu = MenuFactory(date=timezone.now().date())
        serializer = VoteSerializerV1()

        validated_menu = serializer.validate_menu(menu)
        assert validated_menu == menu

    def test_validate_menu_not_today(self):
        tomorrow = timezone.now().date() + timezone.timedelta(days=1)
        menu = MenuFactory(date=tomorrow)
        serializer = VoteSerializerV1()

        with pytest.raises(ValidationError) as exc_info:
            serializer.validate_menu(menu)
        assert "You can only vote for today's menu" in str(exc_info.value)


@pytest.mark.django_db
class TestVoteDetailSerializerV1:
    def setup_method(self):
        self.patcher = patch("django.utils.timezone.localtime")
        self.mock_localtime = self.patcher.start()
        mock_time = datetime.combine(timezone.now().date(), time(10, 0))
        self.mock_localtime.return_value = mock_time

    def teardown_method(self):
        self.patcher.stop()

    def test_serialize_vote_detail(self):
        vote = VoteFactory()
        serializer = VoteDetailSerializerV1(vote)

        assert serializer.data["id"] == vote.id
        assert serializer.data["restaurant_name"] == vote.menu.restaurant.name
        assert serializer.data["menu_date"] == vote.menu.date.isoformat()


@pytest.mark.django_db
class TestVotingResultSerializerV1:
    def test_serialize_voting_result(self):
        menu = MenuFactory()
        result_data = {
            "menu": menu.id,
            "votes_count": 5,
        }
        serializer = VotingResultSerializerV1(result_data)

        assert serializer.data["votes_count"] == result_data["votes_count"]
        assert serializer.data["restaurant_name"] == menu.restaurant.name
