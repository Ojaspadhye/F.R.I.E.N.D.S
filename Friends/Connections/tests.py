from rest_framework.test import APITestCase
from Connections.models import Friend
from Profiles.models import UserProfile
from django.urls import reverse

# Create your tests here.

class MakingConnections(APITestCase):
    '''
    Test for the models setup.

    Things to check:
        > if users are segrigated properly in user1 and user2 asper their primarykeys
        > if data is preserved or the sender data is preserved
        > if status is properly changed
        > if the requests are properly sent
        > if friends properly apper
        > if requests go to blocked addresses
        > if the senders address changes to the new sender if regected entity resends. Probably would do somthing like deletions for simplifing
        > if someone elses friends can be ascessed.
    '''
    from rest_framework.test import APITestCase
from django.urls import reverse

class MakingConnections(APITestCase):

    def setUp(self):

        self.user1 = UserProfile.objects.create_user(
            username="BigOjas",
            email="big@gmail.com",
            password="BigG"
        )

        self.user2 = UserProfile.objects.create_user(
            username="MiniOjas",
            email="mini@gmail.com",
            password="MiniG"
        )

        self.user3 = UserProfile.objects.create_user(
            username="AvgOjas",
            email="avg@gmail.com",
            password="AvgG"
        )

        self.send_url = reverse("sendingrequest")
        self.respond_url = reverse("Respond to request")
        self.get_friends_url = reverse("getfriends")
        self.get_pending_sent_url = reverse("getpendingsent")
        self.get_pending_received_url = reverse("getrecivedpending")

    
    def test_user_ordering(self):
        self.client.force_authenticate(user=self.user2)

        self.client.post(
            self.send_url,
            {"reciverId": self.user1.id},
            format="json"
        )

        relation = Friend.objects.first()

        self.assertTrue(relation.user1.id < relation.user2.id)

    def test_sender_preserved(self):
        self.client.force_authenticate(user=self.user2)

        self.client.post(
            self.send_url,
            {"reciverId": self.user1.id},
            format="json"
        )

        relation = Friend.objects.first()

        self.assertEqual(relation.sender, self.user2)

    
    def test_status_changes_to_accepted(self):
        self.client.force_authenticate(user=self.user2)

        self.client.post(
            self.send_url,
            {"reciverId": self.user1.id},
            format="json"
        )

        relation = Friend.objects.first()

        self.client.force_authenticate(user=self.user1)

        self.client.patch(
            self.respond_url,
            {"requestid": relation.id, "action": "accepted"},
            format="json"
        )

        relation.refresh_from_db()
        self.assertEqual(relation.status, "accepted")


    def test_request_sent_successfully(self):
        self.client.force_authenticate(user=self.user2)

        response = self.client.post(
            self.send_url,
            {"reciverId": self.user1.id},
            format="json"
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Friend.objects.count(), 1)

    
    def test_friends_appear_after_accept(self):
        self.client.force_authenticate(user=self.user2)

        self.client.post(
            self.send_url,
            {"reciverId": self.user1.id},
            format="json"
        )

        relation = Friend.objects.first()

        self.client.force_authenticate(user=self.user1)

        self.client.patch(
            self.respond_url,
            {"requestid": relation.id, "action": "accepted"},
            format="json"
        )

        response = self.client.get(self.get_friends_url)

        self.assertEqual(len(response.data), 1)

    
    def test_block_prevents_new_request(self):
        self.client.force_authenticate(user=self.user2)

        self.client.post(
            self.send_url,
            {"reciverId": self.user1.id},
            format="json"
        )

        relation = Friend.objects.first()

        self.client.force_authenticate(user=self.user1)

        self.client.patch(
            self.respond_url,
            {"requestid": relation.id, "action": "blocked"},
            format="json"
        )

        self.client.force_authenticate(user=self.user2)

        response = self.client.post(
            self.send_url,
            {"reciverId": self.user1.id},
            format="json"
        )

        self.assertEqual(response.status_code, 400)

    
    def test_rejected_request_can_be_resent(self):
        self.client.force_authenticate(user=self.user2)

        self.client.post(
            self.send_url,
            {"reciverId": self.user1.id},
            format="json"
        )

        relation = Friend.objects.first()

        self.client.force_authenticate(user=self.user1)

        self.client.patch(
            self.respond_url,
            {"requestid": relation.id, "action": "rejected"},
            format="json"
        )

        self.client.force_authenticate(user=self.user1)

        self.client.post(
            self.send_url,
            {"reciverId": self.user2.id},
            format="json"
        )

        relation.refresh_from_db()
        self.assertEqual(relation.sender, self.user1)
        self.assertEqual(relation.status, "pending")

    
    def test_cannot_access_others_friends(self):
        self.client.force_authenticate(user=self.user2)

        self.client.post(
            self.send_url,
            {"reciverId": self.user1.id},
            format="json"
        )

        relation = Friend.objects.first()

        self.client.force_authenticate(user=self.user1)

        self.client.patch(
            self.respond_url,
            {"requestid": relation.id, "action": "accepted"},
            format="json"
        )

        # user3 checks their friends
        self.client.force_authenticate(user=self.user3)

        response = self.client.get(self.get_friends_url)

        self.assertEqual(len(response.data), 0)