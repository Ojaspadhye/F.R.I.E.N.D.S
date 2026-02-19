from Profiles.models import UserProfile


def run():
    user = UserProfile()

    print(user.objects.all())