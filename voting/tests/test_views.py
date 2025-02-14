from datetime import datetime, time
from unittest.mock import patch

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from authentication.tests.factories import EmployeeFactory
from restaurants.tests.factories import MenuFactory, MenuItemFactory
from voting.tests.factories import VoteFactory


@pytest.mark.django_db
class TestCreateVoteView:
    def setup_method(self):
        self.client = APIClient()
        self.url = reverse("voting:create-vote")
        self.employee = EmployeeFactory()
        self.client.force_authenticate(user=self.employee)
        self.patcher = patch("django.utils.timezone.localtime")
        self.mock_localtime = self.patcher.start()
        mock_time = datetime.combine(timezone.now().date(), time(10, 0))
        self.mock_localtime.return_value = mock_time

    def teardown_method(self):
        self.patcher.stop()

    def test_create_vote_v1(self):
        menu = MenuFactory(date=timezone.now().date())
        MenuItemFactory(menu=menu)
        data = {"menu": menu.id}

        response = self.client.post(
            self.url, data, HTTP_ACCEPT="application/json; version=1.0"
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["restaurant_name"] == menu.restaurant.name
        assert response.data["menu_date"] == menu.date.isoformat()

    def test_create_vote_v2(self):
        menu = MenuFactory(date=timezone.now().date())
        MenuItemFactory(menu=menu)
        data = {"menu": menu.id}

        response = self.client.post(
            self.url, data, HTTP_ACCEPT="application/json; version=2.0"
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["id"]
        assert response.data["restaurant_name"] == menu.restaurant.name
        assert response.data["menu_date"] == menu.date.isoformat()

    def test_create_vote_for_future_menu(self):
        tomorrow = timezone.now().date() + timezone.timedelta(days=1)
        menu = MenuFactory(date=tomorrow)
        data = {"menu": menu.id}

        response = self.client.post(self.url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "You can only vote for today's menu" in str(response.data)

    def test_create_vote_after_11am(self):
        mock_time = datetime.combine(timezone.now().date(), time(11, 1))
        self.mock_localtime.return_value = mock_time

        menu = MenuFactory(date=timezone.now().date())
        data = {"menu": menu.id}

        response = self.client.post(self.url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Voting is only allowed before 11:00 AM" in str(response.data["detail"])

    def test_create_duplicate_vote(self):
        menu1 = MenuFactory(date=timezone.now().date())
        menu2 = MenuFactory(date=timezone.now().date())
        VoteFactory(employee=self.employee, menu=menu1)

        data = {"menu": menu2.id}
        response = self.client.post(self.url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Vote with this Employee and Date already exists" in str(
            response.data["detail"]
        )


@pytest.mark.django_db
class TestUserVoteHistoryView:
    def setup_method(self):
        self.client = APIClient()
        self.url = reverse("voting:vote-history")
        self.employee = EmployeeFactory()
        self.client.force_authenticate(user=self.employee)
        self.patcher = patch("django.utils.timezone.localtime")
        self.mock_localtime = self.patcher.start()
        mock_time = datetime.combine(timezone.now().date(), time(10, 0))
        self.mock_localtime.return_value = mock_time

    def teardown_method(self):
        self.patcher.stop()

    def test_get_vote_history_v1(self):
        vote = VoteFactory(employee=self.employee)
        MenuItemFactory(menu=vote.menu)

        response = self.client.get(
            self.url, HTTP_ACCEPT="application/json; version=1.0"
        )

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert (
            response.data["results"][0]["restaurant_name"] == vote.menu.restaurant.name
        )
        assert response.data["results"][0]["menu_date"] == vote.menu.date.isoformat()

    def test_get_vote_history_v2(self):
        vote = VoteFactory(employee=self.employee)
        MenuItemFactory(menu=vote.menu)

        response = self.client.get(
            self.url, HTTP_ACCEPT="application/json; version=2.0"
        )

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["id"] == vote.id
        assert (
            response.data["results"][0]["restaurant_name"] == vote.menu.restaurant.name
        )
        assert response.data["results"][0]["menu_date"] == vote.menu.date.isoformat()

    def test_get_vote_history_empty(self):
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 0


@pytest.mark.django_db
class TestTodayResultsView:
    def setup_method(self):
        self.client = APIClient()
        self.url = reverse("voting:today-results")
        self.employee = EmployeeFactory()
        self.client.force_authenticate(user=self.employee)
        self.patcher = patch("django.utils.timezone.localtime")
        self.mock_localtime = self.patcher.start()
        mock_time = datetime.combine(timezone.now().date(), time(10, 0))
        self.mock_localtime.return_value = mock_time

    def teardown_method(self):
        self.patcher.stop()

    def test_get_today_results_v1(self):
        menu1 = MenuFactory(date=timezone.now().date())
        menu2 = MenuFactory(date=timezone.now().date())
        MenuItemFactory(menu=menu1)
        MenuItemFactory(menu=menu2)

        # Create 3 votes for menu1 and 2 votes for menu2
        for _ in range(3):
            VoteFactory(menu=menu1)
        for _ in range(2):
            VoteFactory(menu=menu2)

        response = self.client.get(
            self.url, HTTP_ACCEPT="application/json; version=1.0"
        )

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2
        assert response.data["results"][0]["votes_count"] == 3
        assert response.data["results"][0]["restaurant_name"] == menu1.restaurant.name
        assert response.data["results"][1]["votes_count"] == 2
        assert response.data["results"][1]["restaurant_name"] == menu2.restaurant.name

    def test_get_today_results_v2(self):
        menu1 = MenuFactory(date=timezone.now().date())
        menu2 = MenuFactory(date=timezone.now().date())
        MenuItemFactory(menu=menu1)
        MenuItemFactory(menu=menu2)

        for _ in range(3):
            VoteFactory(menu=menu1)
        for _ in range(2):
            VoteFactory(menu=menu2)

        response = self.client.get(
            self.url, HTTP_ACCEPT="application/json; version=2.0"
        )

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2
        assert response.data["results"][0]["votes_count"] == 3
        assert response.data["results"][0]["restaurant_name"] == menu1.restaurant.name
        assert response.data["results"][1]["votes_count"] == 2
        assert response.data["results"][1]["restaurant_name"] == menu2.restaurant.name

    def test_get_today_results_empty(self):
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 0

    def test_get_today_results_exclude_other_days(self):
        today = timezone.now().date()
        tomorrow = today + timezone.timedelta(days=1)

        today_menu = MenuFactory(date=today)
        tomorrow_menu = MenuFactory(date=tomorrow)
        MenuItemFactory(menu=today_menu)
        MenuItemFactory(menu=tomorrow_menu)

        VoteFactory(menu=today_menu)

        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["votes_count"] == 1
        assert (
            response.data["results"][0]["restaurant_name"] == today_menu.restaurant.name
        )
