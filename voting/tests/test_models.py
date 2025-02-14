from datetime import datetime, time
from unittest.mock import patch

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from authentication.tests.factories import EmployeeFactory
from restaurants.tests.factories import MenuFactory
from voting.tests.factories import VoteFactory


@pytest.mark.django_db
class TestVoteModel:
    def setup_method(self):
        self.patcher = patch("django.utils.timezone.localtime")
        self.mock_localtime = self.patcher.start()
        mock_time = datetime.combine(timezone.now().date(), time(10, 0))
        self.mock_localtime.return_value = mock_time

    def teardown_method(self):
        self.patcher.stop()

    def test_create_vote(self):
        vote = VoteFactory()
        assert vote.pk is not None
        assert vote.employee
        assert vote.menu
        assert vote.date == timezone.now().date()

    def test_vote_str(self):
        vote = VoteFactory()
        expected_str = f"{vote.employee} voted for {vote.menu} on {vote.date}"
        assert str(vote) == expected_str

    def test_one_vote_per_day_constraint(self):
        employee = EmployeeFactory()
        menu1 = MenuFactory()
        menu2 = MenuFactory()

        VoteFactory(employee=employee, menu=menu1)

        with pytest.raises(ValidationError):
            VoteFactory(employee=employee, menu=menu2)

    def test_vote_only_for_today(self):
        tomorrow = timezone.now().date() + timezone.timedelta(days=1)
        MenuFactory(date=tomorrow)

        with pytest.raises(ValidationError) as exc_info:
            VoteFactory(date=tomorrow)
        assert "You can only vote for today's menu" in str(exc_info.value)

    def test_vote_before_11am(self):
        mock_time = datetime.combine(timezone.now().date(), time(10, 0))
        self.mock_localtime.return_value = mock_time

        vote = VoteFactory()
        assert vote.pk is not None

    def test_vote_after_11am(self):
        mock_time = datetime.combine(timezone.now().date(), time(11, 1))
        self.mock_localtime.return_value = mock_time

        with pytest.raises(ValidationError) as exc_info:
            VoteFactory()
        assert "Voting is only allowed before 11:00 AM" in str(exc_info.value)
