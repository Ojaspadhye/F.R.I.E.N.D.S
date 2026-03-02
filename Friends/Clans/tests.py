from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from datetime import timedelta
import uuid
from Clans.models import Clan, Members
from Profiles.models import UserProfile


class ClanViewTests(APITestCase):
    def setUp(self):
        # first user
        self.username1 = "BigOjas"
        self.password1 = "BigG"
        self.email1 = "BigG@gmail.com"

        self.user1 = UserProfile.objects.create_user(username=self.username1, email=self.email1, password=self.password1)

        payload_user1 = {
            "username_email": self.username1,
            "password": self.password1
        }
        

        # second user
        self.username2 = "TinyOjas"
        self.password2 = "TinyG"
        self.email2 = "TinyG@gmail.com"

        self.user2 = UserProfile.objects.create_user(username=self.username2, email=self.email2, password=self.password2)


        payload_user2 = {
            "username_email": self.username2,
            "password": self.password2
        }

        # create clan1 public default
        self.name1 = "SIAM"
        self.clan1 = Clan.objects.create(
            name=self.name1,
            creator=self.user1
        )

        # create clan2 private
        self.name2 = "4 Brain Cells"
        self.clan2 = Clan.objects.create(
            name=self.name2,
            visibility="Private",
            creator=self.user2
        )


        # Urls
        self.owned_url = reverse("user-owned-clans")
        self.joined_url = reverse("user-joined-clans")
        self.get_popular_url = reverse("popular-clans")
        self.search_byname_url = reverse("clan-by-name")
        self.get_by_age_url = reverse("clan-by-age-range")
        self.login_url = reverse("user_login")

        # Login
        response1 = self.client.post(
            self.login_url,
            payload_user1,
            format="json"
        )
        self.access1 = response1.data["AccessToken"]

        response2 = self.client.post(
            self.login_url,
            payload_user2,
            format="json"
        )
        self.access2 = response2.data["AccessToken"]

        # Make User 2 join SIAM
        Members.objects.create(
            clan=self.clan1,
            member=self.user1
        )


    def test_owned_clans_authenticated(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access1}')
        response = self.client.get(self.owned_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "SIAM")
        self.assertEqual(response.data[0]["creator"], self.user1.id)

    def test_owned_clans_requires_authentication(self):
        self.client.credentials()
        response = self.client.get(self.owned_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_owned_clans_returns_correct_user(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access2}')
        response = self.client.get(self.owned_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "4 Brain Cells")
        self.assertEqual(response.data[0]["creator"], self.user2.id)

    def test_popular_clans(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access1}')
        response = self.client.get(self.get_popular_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["name"], "SIAM")

    def test_search_by_name(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access1}')
        response = self.client.get(self.search_byname_url, {"name": "SIAM"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "SIAM")

    def test_clan_by_age_range(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access1}')
        response = self.client.get(self.get_by_age_url, {"min_limit": 0, "max_limit": 10})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [c["name"] for c in response.data]
        self.assertIn("SIAM", names)
        self.assertIn("4 Brain Cells", names)
        self.assertNotIn("OldClan", names)


    