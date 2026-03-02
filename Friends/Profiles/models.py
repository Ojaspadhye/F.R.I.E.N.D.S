from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
import secrets
from django.dispatch import receiver
from django.db.models.signals import post_save
from Friends import settings

def generate_user_id():
    return secrets.randbits(63)


# Create your models here.
class CustomUserManager(BaseUserManager):
    def create_user(self, username: str, email: str, password=None, **extra_fields):
        if not username:
            raise ValueError("Username must be provided.")
        if not email:
            raise ValueError("Email must be provided.")

        email    = self.normalize_email(email).lower()
        username = username.strip().lower()

        user = self.model(username=username, email=email, **extra_fields)

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save(using=self._db)
        return user

    def create_superuser(self, username: str, email: str, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_active", True)

        if not extra_fields.get("is_staff"):
            raise ValueError("Superuser must have is_staff=True.")

        return self.create_user(username, email, password, **extra_fields)


class UserProfile(AbstractBaseUser):
    id = models.BigIntegerField(primary_key=True, default=generate_user_id)
    
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    
    first_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    
    date_joined = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(blank=True, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD  = "username"
    REQUIRED_FIELDS = ["email"]

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
        ordering            = ["id"]

    def __str__(self):
        return f"{self.username} <{self.email}>"

    def get_full_name(self):
        return f"{self.first_name or ''} {self.last_name or ''}".strip() or self.username

    def get_short_name(self):
        return self.first_name or self.username

class OTPVerificationManager(models.Manager):
    def create_otp(self, user):
        """Purge existing OTPs for this user and issue a fresh one."""
        self.filter(user=user).delete()
        return self.create(user=user, otp=self._generate_otp())

    def get_valid(self, email):
        """Return the latest non-expired OTP for a given email, or None."""
        record = (
            self.filter(user__email=email)
            .select_related("user")
            .order_by("-created_at")
            .first()
        )
        if record is None or record.is_expired():
            return None
        return record

    def purge_expired(self):
        cutoff = timezone.now() - timedelta(minutes=settings.OTP_EXPIRY_MINUTES)
        deleted, _ = self.filter(created_at__lt=cutoff).delete()
        return deleted

    @staticmethod
    def _generate_otp():
        return f"{secrets.randbelow(900_000) + 100_000:06d}"
    


class OTPVerification(models.Model):
    user       = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="otps",
    )
    otp        = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = OTPVerificationManager()

    class Meta:
        verbose_name        = "OTP Verification"
        verbose_name_plural = "OTP Verifications"
        ordering            = ["-created_at"]

    def __str__(self):
        return f"OTP for {self.user.email}"

    def is_expired(self) -> bool:
        return timezone.now() > self.created_at + timedelta(minutes=settings.OTP_EXPIRY_MINUTES)


    '''
    The Idea is that User data will be in two tables
    one being the authentication and core table will queried only with authentication
    The other is this one which contains the metadata with items: Queried all time for dashboard and basic functions
    Also is sutomatioally generated the moment the core auth model USerProfile is created
        > user id
        > username
        > pfp
        > last active
        > Discription
        > Friends Count
        > Later Verification badges roles
    '''



class MetaProfileData(models.Model):
    user = models.OneToOneField(
        UserProfile,
        on_delete=models.CASCADE,
        db_index=True
    )
    username = models.CharField(max_length=100, unique=True, db_index=True)

    pfp = models.ImageField(upload_to="avatars/", blank=True, null=True)
    banner = models.ImageField(upload_to="banners/", blank=True, null=True)

    bio = models.TextField(max_length=100, blank=True, null=True)

    birth_date = models.DateField(blank=True, null=True)

    latitude = models.CharField(max_length=20, blank=True, null=True)
    longitude = models.CharField(max_length=20, blank=True, null=True)

    friends_count = models.BigIntegerField(default=0)
    last_login = models.DateTimeField(blank=True, null=True)

    BADGES = (
        ('batman', 'batman'),
        ('joker', 'joker'),
        ('alfred', 'alfred'),
        ('nightwing', 'nightwing'),
        ('penguin', 'penguin'),
        ('riddler', 'riddler')
    )

    badges = models.CharField(max_length=10, choices=BADGES, default='riddler')

    THEME = (
        ('dark', 'dark'),
        ('light', 'light')
    )

    theme = models.CharField(max_length=6, choices=THEME, default='light')


    class Meta:
        verbose_name = "MetaUserProfile"
        verbose_name_plural = "MetaUserProfiles"
    


    def __str__(self):
        return f"{self.username} ({self.user.id})"


@receiver(post_save, sender=UserProfile)
def create_user_meta(sender, instance, created, **extra_arguments):
    if created:
        MetaProfileData.objects.create(
            user=instance,
            username = instance.username
        )
    

@receiver(post_save, sender=UserProfile)
def match_username(sender, instance,  created, **extra_arguments):
    if not created:
        MetaProfileData.objects.filter(user=instance).update(username=instance.username)