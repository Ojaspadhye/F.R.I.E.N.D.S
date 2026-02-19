from django.test import TestCase
from Profiles.models import UserProfile

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
        self.assertFalse(user.is_staff)

    
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