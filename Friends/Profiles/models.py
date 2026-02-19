from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser


# Create your models here.
class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **args):
        if not username:
            raise ValueError("Username Not provided")
        
        if not email:
            raise ValueError("Email Id not provided")
        
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **args)

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save(using=self._db)

        return user



class UserProfile(AbstractBaseUser):
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    info = models.TextField(max_length=200, blank=True)
    #is_staff = models.BooleanField(default=False) -> Not implemented yet
    date_joined = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(blank=True, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
