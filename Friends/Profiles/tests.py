from django.test import TestCase
from rest_framework.test import APITestCase
from Profiles.models import UserProfile
from django.urls import reverse
from rest_framework import status

# Create your tests here.

class UserProfileModel(TestCase):

    def setUp(self):
        self.user = UserProfile.objects.create_user(
            username="Test",
            email="test@example.com",
            password="Hero--9993",
            first_name="Ojas",
            last_name="Backend Dev",
            info="I am the backend dev"
        )

    
    def test_creation(self):
        user = self.user

        self.assertEqual(user.username, "Test")
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.first_name, "Ojas")
        self.assertEqual(user.last_name, "Backend Dev")
        self.assertEqual(user.info, "I am the backend dev")
        self.assertTrue(user.is_active)

    
    def test_password(self):
        user = self.user

        self.assertNotEqual(user.password, "Hero--9993")
        self.assertTrue(user.check_password("Hero--9993"))

    def test_email_uniqueness(self):
        with self.assertRaises(Exception):
            UserProfile.objects.create_user(
                username="Ojas2",
                email="test@example.com",
                password="AnotherPass123"
            )

    
    def test_user_str(self):
        self.assertEqual(str(self.user), "Test")



class UserBasicAuth(APITestCase):

    def setUp(self):
        self.username = "TestUser"
        self.password = "My_Fat_cock"
        self.email = "Test@TestUser.com"

        self.login_URL = reverse('user_login')
        self.signup_URL = reverse('user_signup')
        self.get_profile_URL = reverse('user_profile') 

    def test_signup(self):
        payload = {
            "username": self.username,
            "password": self.password,
            "email_id": self.email
        }

        response = self.client.post(
            self.signup_URL, 
            payload, 
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_login_get_profile(self):

        UserProfile.objects.create_user(
            username=self.username,
            email=self.email,
            password=self.password
        )

        payload = {
            "username_email": self.username,
            "password": self.password
        }

        response = self.client.post(
            self.login_URL,
            payload,
            format="json"
        )

        access = response.data["AccessToken"]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('AccessToken', response.data)
        self.assertIn('RefreshToken', response.data)

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')
        profile_response = self.client.get(self.get_profile_URL)

        self.assertEqual(profile_response.status_code, status.HTTP_200_OK)
        self.assertEqual(profile_response.data['username'], self.username)
