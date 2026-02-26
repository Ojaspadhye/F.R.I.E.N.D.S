from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from datetime import timedelta
import uuid
from Clans.models import Clan, Members
from Profiles.models import UserProfile
from django.test import TestCase
User = get_user_model()


class ClanViewTests(APITestCase):
    def setUp(self):
        # Create two users
        self.user1 = User.objects.create_user(
            username="user1",
            email=f"user1_{uuid.uuid4()}@example.com",
            password="password123"
        )
        self.user2 = User.objects.create_user(
            username="user2",
            email=f"user2_{uuid.uuid4()}@example.com",
            password="password456"
        )

        # Create profiles linked to the users
        self.profile1 = UserProfile.objects.create(user=self.user1, age=20)
        self.profile2 = UserProfile.objects.create(user=self.user2, age=22)

        # Create some clans
        self.clan1 = Clan.objects.create(name="ClanAlpha", owner=self.profile1)
        self.clan2 = Clan.objects.create(name="ClanBeta", owner=self.profile2)

        # Optional: add members
        self.clan1.members.add(self.profile2)  # profile2 joins clan1

    # ----------------------------
    # Owned Clans
    # ----------------------------
    def test_get_owned_clans_authenticated(self):
        self.client.login(username="owner", password="testpass123")
        url = "/api/clans/owned/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_get_owned_clans_unauthenticated(self):
        url = "/api/clans/owned/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # ----------------------------
    # Joined Clans
    # ----------------------------
    def test_get_joined_clans_authenticated(self):
        self.client.login(username="member", password="testpass123")
        url = "/api/clans/joined/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Alpha")

    def test_get_joined_clans_unauthenticated(self):
        url = "/api/clans/joined/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # ----------------------------
    # Popular Clans
    # ----------------------------
    def test_get_popular_clans(self):
        url = "/api/clans/popular/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_popular_clans_sorted(self):
        url = "/api/clans/popular/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["name"], "Alpha")

    # ----------------------------
    # Clans by Age Range
    # ----------------------------
    def test_get_clan_by_age_range_valid(self):
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)

        url = f"/api/clans/by-age-range/?start_date={yesterday}&end_date={tomorrow}"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 2)

    def test_get_clan_by_age_range_missing_params(self):
        url = "/api/clans/by-age-range/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    # ----------------------------
    # Clans by Name
    # ----------------------------
    def test_get_clan_by_name_valid(self):
        url = "/api/clans/by-name/?name=Alpha"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Alpha")

    def test_get_clan_by_name_invalid(self):
        url = "/api/clans/by-name/?name=Unknown"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)