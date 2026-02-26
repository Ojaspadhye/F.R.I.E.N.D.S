from rest_framework import serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from Clans.models import Clan, Members
from django.db.models import Count
from Profiles.models import UserProfile
from rest_framework.response import Response

# Create your views here.

'''
To search clans

Filters:
    > Where user has joined
    > Most popular to least popular (currently on strength)
    > recent or older on date
    > by straightup name
'''

class ClanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clan
        fields = "__all__"


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_users_owned_clans(request):
    user = request.user
    user_owned_clans = Clan.objects.request_users_owned_clan(user)

    serializer = ClanSerializer(user_owned_clans, many=True)

    return Response(serializer.data, status=200)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_joined_clans(request):
    user = request.user
    memberships = Members.objects.request_user_joined_clan(user)

    clans = Clan.objects.filter(id__in=memberships.values_list("clan_id", flat=True))

    serializer = ClanSerializer(clans, many=True)

    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([AllowAny])
def get_popular_clan(request):
    clans = Clan.objects.annotate(
        member_count=Count("clan_members")
    ).order_by("-member_count")

    serializer = ClanSerializer(clans, many=True)

    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([AllowAny])
def get_clan_by_agerange(request):
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    clans = Clan.objects.request_clan_age_range(start_date, end_date)

    serializer = ClanSerializer(clans, many=True)

    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([AllowAny])
def get_clan_by_name(request):
    clan_name = request.GET.get("name")

    clans = Clan.objects.request_public_clan_name(clan_name)

    serializer = ClanSerializer(clans, many=True)

    return Response(serializer.data)