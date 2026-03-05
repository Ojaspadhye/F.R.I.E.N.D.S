from django.db import models
from django.db.models import Q
from django.dispatch import receiver
from django.db.models.signals import post_save
import secrets
from django.utils import timezone

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
def generate_connection_id():
    return secrets.randbits(63)

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



    def respond(self, friendship, current_user, action):

        if action not in ['accepted', 'rejected', 'blocked']:
            raise ValueError("Invalid action.")

        sender = friendship.sender
        receiver = (
            friendship.user2 if friendship.user1 == sender
            else friendship.user1
        )

        if action in ['accepted', 'rejected']:
            if current_user != receiver:
                raise ValueError("Only receiver can respond.")

        if action == 'blocked':
            if current_user not in [sender, receiver]:
                raise ValueError("You are not part of this connection.")

        friendship.status = action

        if action == "accepted":
            friendship.accepted_at = timezone.now()

        elif action == "rejected":
            friendship.rejected_at = timezone.now()

        elif action == "blocked":
            friendship.blocked_at = timezone.now()

        friendship.save()
        return friendship


    def get_friends(self, user):
        return self.filter(
            Q(user1=user) | Q(user2=user),
            status='accepted'
        ).order_by('-accepted_at')


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
    


# Major set data of connections. Genral Lifecycle for setting connections.
class Friend(models.Model):
    id = models.BigIntegerField(primary_key=True, default=generate_connection_id)

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

    accepted_at = models.DateTimeField(blank=True, null=True)
    rejected_at = models.DateTimeField(blank=True, null=True)
    blocked_at = models.DateTimeField(blank=True, null=True)
    unfriend_at = models.DateTimeField(blank=True, null=True)
    last_interaction_at = models.DateTimeField(blank=True, null=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = FriendManager()

    class Meta:
        verbose_name = "FriendShip"
        verbose_name_plural = "FriendShips"
        unique_together = ('user1', 'user2')
        ordering = ['-created_at'] 
        


# Block and Toxcicity prevention logic
class Block(models.Model):
    blocker_user = models.ForeignKey(
        'Profiles.UserProfile',
        on_delete=models.CASCADE,
        related_name='blocker_user'
    )

    blocked_user = models.ForeignKey(
        'Profiles.UserProfile',
        on_delete=models.CASCADE,
        related_name='Blocked_user'
    )

    blocked_at = models.DateTimeField(auto_now_add=True)
    unblocked_at = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)


    friend = models.ForeignKey(
        Friend,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='blocks'
    )

    class Meta:
        unique_together = ('blocker_user', 'blocked_user')



class FriendMeta(models.Model):
    connection = models.OneToOneField(
        to=Friend,
        on_delete=models.CASCADE,
        db_index=True
    )

    NOTIFICATION_CHOICE = (
        ('email', 'email'),
        ('message', 'message')
    )

    TAGS = (
        ('work', 'work'),
        ('classmates', 'classmates'),
        ('sports', 'sports'),
        ('collage', 'collage')
    )

    user1_notification = models.CharField(max_length=10, choices=NOTIFICATION_CHOICE, default='email')
    user2_notification = models.CharField(max_length=10, choices=NOTIFICATION_CHOICE, default='email')

    user1_muted = models.BooleanField(default=False)
    user2_muted = models.BooleanField(default=False)

    theme = models.ImageField(upload_to="text_theme/", blank=True, null=True)
    
    user1_nickname = models.CharField(max_length=100, blank=True, null=True)
    user2_nickname = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = "MetaFriendship"
        verbose_name_plural = "MetaFriendships"
    
    def __str__(self):
        return self.connction


@receiver(post_save, sender=Friend)
def create_user_meta(sender, instance, created, **extra_arguments):
    if created:
        FriendMeta.objects.create(
            connection=instance
        )
    

@receiver(post_save, sender=Friend)
def match_username(sender, instance,  created, **extra_arguments):
    if not created:
        FriendMeta.objects.filter(connection=instance)