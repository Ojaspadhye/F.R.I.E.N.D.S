from django.db import models
from datetime import datetime

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

    def request_clan_age_range(self, start_date, end_date):
        if not start_date or not end_date:
            return self.none()

        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()

        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

        return self.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        )
        


class Clan(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(max_length=500, null=True)

    VISIBILITY_CHOICES = (
        ('Private', 'private'),
        ('Public', 'public')
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
        ('Active', 'active'),
        ('Inactive', 'inactive')
    )
    activity = models.CharField(max_length=10, choices=ACTIVITY_CHOICES, default='active')

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


