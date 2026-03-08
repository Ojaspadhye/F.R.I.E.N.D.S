from Clans.models import Clan, Members
from django.db import transaction


def create_clan_service(user, data):
    with transaction.atomic():
        clan = Clan.objects.create_clan(
        name=data["name"],
        discription=data["data"],
        creator=user
    )

def get_user_owned_clans(user):
    try: 
        clans = Clan.objects.request_users_owned_clan(user)
    except Clan.DoesNotExist:
        raise f"The user dose not own any clan"
    
    return clans


def get_user_joined_clans(user):
    try:
        clans = Clan.objects.request_users_owned_clan(user)
    except Members.DoesNotExist:
        raise f"The user hasnt joined ant clan"
    
    return clans

def get_famous_clans():
    try:
        clans = Clan.objects.request_popular_clan()
    except Clan.DoesNotExist:
        raise f"The clan doesnot exist"
    
    return clans