from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from datetime import datetime
from django.utils import timezone
from datetime import timedelta
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete

# Create your models here.

'''
To add Managers for clans.

>  Clans Table
>  Members Table

Points to implement:
    > Time stamps for clans creations updates
    > Name of clan
    > Creator Id
    > ownership
    > Goining code hashed
    > Pepes joining the clan
    > Pepes being groups positions
        > creator (absolute poewer)
        > owner
        > bots
        > managers
        > Normal peps 
        > guests
'''

class ClanManager(models.Manager):
    def request_public_clan_name(self, clan_name):
        if not clan_name:
            return self.none()

        return self.filter(
            name=clan_name,
            visibility='public'
        )

    def request_users_owned_clan(self, user):
        if not user:
            return self.none()

        return self.filter(creator=user)
        
    def request_clan_age_range(self, min_limit: int, max_limit: int):
        if min_limit is None or max_limit is None:
            return self.none()

        now = timezone.now()

        start_date = now - timedelta(days=max_limit)
        end_date = now - timedelta(days=min_limit)

        return self.filter(created_at__gte=start_date, created_at__lte=end_date)
    
    def request_popular_clan(self):
        return self.order_by('-member_count')
    
    def create_clan(self, name, creator, visibility='public', joining_code=None):
        if joining_code:
            joining_code = make_password(joining_code)

        return self.create(
            name=name.strip(),
            creator_id=creator.id,
            visibility=visibility,
            joining_code=joining_code
        )
    
    def check_code(self, clan, joining_code):
        clan_code = clan.joining_code
        return check_password(clan_code, joining_code)


class Clan(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(max_length=500, null=True)

    VISIBILITY_CHOICES = (
        ('private', 'private'),
        ('public', 'public')
    )
    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default='public')

    creator = models.ForeignKey(
        'Profiles.UserProfile',
        on_delete=models.SET_NULL,
        related_name='creators',
        null=True
    )

    joining_code = models.CharField(max_length=100, blank=True, null=True)

    ACTIVITY_CHOICES = (
        ('active', 'active'),
        ('inactive', 'inactive')
    )
    activity = models.CharField(max_length=10, choices=ACTIVITY_CHOICES, default='active')

    member_count = models.BigIntegerField(default=0)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = ClanManager()


class MembersManager(models.Manager):
    def managers(self):
        return self.filter(roles='manager')

    def bots(self):
        return self.filter(roles='bot')

    def members_in_clan(self, clan):
        if not clan:
            return self.none()
        return self.filter(clan=clan)

    def request_user_joined_clan(self, user):
        if not user:
            return self.none()

        return self.filter(
            member=user
        ).exclude(roles='creator')


class Members(models.Model):
    ROLES = (
        ('Creator', 'creator'),
        ('Manager', 'manager'),
        ('Bot', 'bot'),
        ('Normal', 'normal'),
        ('Guest', 'guest')
    )

    clan = models.ForeignKey(
        Clan,
        on_delete=models.CASCADE,
        related_name='clan_members'
    )

    member = models.ForeignKey(
        'Profiles.UserProfile',
        on_delete=models.CASCADE,
        related_name='clan_member_of'
    )

    roles = models.CharField(max_length=10, choices=ROLES, default='normal')
    joined_at = models.DateTimeField(auto_now_add=True)
    left_at = models.DateTimeField(null=True, blank=True)

    objects = MembersManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['clan', 'member'],
                name='unique_clan_member'
            )
        ]


@receiver(post_save, sender=Members)
def update_member_count_increment(sender, instance, created, **kwargs):
    member_count = Members.objects.filter(clan=instance.clan, left_at__isnull=True).count()
    Clan.objects.filter(id=instance.clan).update(member_count=member_count)


@receiver(post_delete, sender=Members)
def update_member_count_decrement(sender, instance, **kwargs):
    member_count = Members.objects.filter(clan=instance.clan, left_at__isnull=True).count()
    Clan.objects.filter(id=instance.clan).update(member_count=member_count)