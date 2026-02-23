from django.db import models
from django.db.models import Q

# Create your models here.
'''
The reson for keeping the user1 user2 is to keep them in a proper order(ascending), and keep the data of who sent the request we have the another sender column in the table.

Let sender have id == 1 and the reciver id == 2
now when the relation is setup id 1 will be put into user1 and the id 2 will be put in the user 2
and because the sender == id1 it 1 will be put in the sender

now if id 2 tries sending the request to id 1 
it will much easy to flag it down cuz we would just check id 2 in the user2 and id1 un user1


otherwise there might be a chase where redundante requests could be made


This is what i done either this works or i am fucking stupid
'''



from django.db import models
from django.db.models import Q


class FriendManager(models.Manager):
    def send_request(self, sender, receiver):
        if sender == receiver:
            raise ValueError("You cannot send a request to yourself.")
        user1, user2 = sorted([sender, receiver], key=lambda x: x.id)

        existing = self.filter(user1=user1, user2=user2).first()

        if existing:
            if existing.status == 'blocked':
                raise ValueError("This relationship is blocked.")

            elif existing.status == 'pending':
                raise ValueError("Friend request already pending.")

            elif existing.status == 'accepted':
                raise ValueError("Friendship already eexists.")

            elif existing.status == 'rejected':
                existing.sender = sender
                existing.status = 'pending'
                existing.save()
                return existing

        return self.create(
            user1=user1,
            user2=user2,
            sender=sender,
            status='pending'
        )



    def responding_request(self, request_obj, current_user, action):
        if action not in ['accepted', 'rejected', 'blocked']:
            raise ValueError("Invalid action.")

        sender = request_obj.sender
        receiver = request_obj.user2 if request_obj.user1 == sender else request_obj.user1

        if action in ['accepted', 'rejected']:
            if current_user != receiver:
                raise ValueError("Who are you")

        if action == 'blocked':
            if current_user not in [sender, receiver]:
                raise ValueError("You are blocked")

        request_obj.status = action
        request_obj.save()
        return request_obj


    def get_friends(self, user):
        relations = self.filter(
            Q(user1=user) | Q(user2=user),
            status='accepted'
        )

        friends = []

        for relation in relations:
            friends.append(
                relation.user2 if relation.user1 == user else relation.user1
            )
        return friends


    def sent_ispending(self, user):
        return self.filter(
            sender=user,
            status='pending'
        )


    def received_ispending(self, user):
        return self.filter(
            Q(user1=user) | Q(user2=user),
            status='pending'
        ).exclude(sender=user)
    



class Friend(models.Model):
    user1 = models.ForeignKey(
        'Profiles.UserProfile',
        on_delete=models.CASCADE,
        related_name='friend_user1'
    )

    user2 = models.ForeignKey(
        'Profiles.UserProfile',
        on_delete=models.CASCADE,
        related_name='friend_user2'
    )

    sender = models.ForeignKey(
        'Profiles.UserProfile',
        on_delete=models.CASCADE,
        related_name='sent_friend_requests'
    )

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('blocked', 'Blocked'),
        ('rejected', 'Rejected'),
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = FriendManager()

    class Meta:
        unique_together = ('user1', 'user2')