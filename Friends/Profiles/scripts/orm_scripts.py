from Profiles.models import UserProfile


def run():
    user = UserProfile.objects.filter(username="P0")

    print(user.set_password("My fat cock"))