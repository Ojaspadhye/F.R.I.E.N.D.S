from celery import shared_task
from Profiles.models import UserProfile

@shared_task
def send_friends_notification_async(user, message):
    print(f"Notify {user.username}: {message}") # for simokicity and currentuse