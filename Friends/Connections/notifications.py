from celery import shared_task
from Profiles.models import UserProfile


@shared_task
def send_friends_notification_async(user: int, message):
    user = UserProfile.objects.get(id=user)
    print(f"Notify {user.username}: {message}") # for simokicity and currentuse