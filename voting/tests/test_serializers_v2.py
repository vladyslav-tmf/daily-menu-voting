from datetime import datetime, time
from unittest.mock import patch

import pytest
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from restaurants.tests.factories import MenuFactory, MenuItemFactory
from voting.api.v2.serializers import (
    VoteDetailSerializerV2,
    VoteSerializerV2,
    VotingResultSerializerV2,
)
from voting.tests.factories import VoteFactory


@pytest.mark.django_db
class TestVoteSerializerV2:
    def setup_method(self):
        self.patcher = patch("django.utils.timezone.localtime")
        self.mock_localtime = self.patcher.start()
        mock_time = datetime.combine(timezone.now().date(), time(10, 0))
        self.mock_localtime.return_value = mock_time

    def teardown_method(self):
        self.patcher.stop()

    def test_serialize_vote(self):
        vote = VoteFactory()
        serializer = VoteSerializerV2(vote)

        assert serializer.data["id"] == vote.id
        assert serializer.data["menu"] == vote.menu.id
        assert serializer.data["date"] == vote.date.isoformat()

    def test_validate_menu_today(self):
        menu = MenuFactory(date=timezone.now().date())
        serializer = VoteSerializerV2()

        validated_menu = serializer.validate_menu(menu)
        assert validated_menu == menu

    def test_validate_menu_not_today(self):
        tomorrow = timezone.now().date() + timezone.timedelta(days=1)
        menu = MenuFactory(date=tomorrow)
        serializer = VoteSerializerV2()

        with pytest.raises(ValidationError) as exc_info:
            serializer.validate_menu(menu)
        assert "You can only vote for today's menu" in str(exc_info.value)


@pytest.mark.django_db
class TestVoteDetailSerializerV2:
    def setup_method(self):
        self.patcher = patch("django.utils.timezone.localtime")
        self.mock_localtime = self.patcher.start()
        mock_time = datetime.combine(timezone.now().date(), time(10, 0))
        self.mock_localtime.return_value = mock_time

    def teardown_method(self):
        self.patcher.stop()

    def test_serialize_vote_detail(self):
        vote = VoteFactory()
        MenuItemFactory(menu=vote.menu)
        serializer = VoteDetailSerializerV2(vote)

        assert serializer.data["id"] == vote.id
        assert serializer.data["menu"]["id"] == vote.menu.id
        assert serializer.data["menu"]["restaurant"] == str(vote.menu.restaurant)
        assert serializer.data["date"] == vote.date.isoformat()
        assert serializer.data["employee_email"] == vote.employee.email
        assert serializer.data["employee_name"] == vote.employee.get_full_name()


@pytest.mark.django_db
class TestVotingResultSerializerV2:
    def test_serialize_voting_result(self):
        menu = MenuFactory()
        MenuItemFactory(menu=menu)
        result_data = {
            "menu": menu.id,
            "votes_count": 5,
        }
        context = {
            "results": [
                {"votes_count": 5},
                {"votes_count": 5},
            ]
        }
        serializer = VotingResultSerializerV2(result_data, context=context)

        assert serializer.data["menu_id"] == menu.id
        assert serializer.data["votes_count"] == result_data["votes_count"]
        assert serializer.data["restaurant_name"] == menu.restaurant.name
        assert serializer.data["menu_details"]["id"] == menu.id
        assert serializer.data["percentage"] == 50.0

    def test_serialize_voting_result_zero_total_votes(self):
        menu = MenuFactory()
        MenuItemFactory(menu=menu)
        result_data = {
            "menu": menu.id,
            "votes_count": 0,
        }
        context = {"results": []}
        serializer = VotingResultSerializerV2(result_data, context=context)

        assert serializer.data["percentage"] == 0
