from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from Clans.models import Clan, Members
from django.db.models import Count
from Profiles.models import UserProfile
from rest_framework.response import Response
from Clans.services import get_user_owned_clans, get_user_joined_clans, get_famous_clans
from Clans.pagination import UserOwnedClansPagination, UserJoinedClansPaginaton, PopularClanPagination
from Clans.serializer import ClansSerializer, UserJoinedClansSerializer

# Create your views here.

'''
To search clans

Filters:
    > Where user has joined
    > Most popular to least popular (currently on strength)
    > recent or older on date
    > by straightup name
'''



@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_users_owned_clans_views(request):
    user = request.user
    
    clans = get_user_owned_clans(user)

    paginator = UserOwnedClansPagination()
    result = paginator.paginate_queryset(clans, request)

    serialized = ClansSerializer(result, many=True)

    return paginator.get_paginated_response(serialized.data)



@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_joined_clans(request):
    user = request.user
    membership = get_user_joined_clans(user)

    pagintor = UserJoinedClansPaginaton()
    result = pagintor.paginate_queryset(membership, request)

    serialized = UserJoinedClansSerializer(result, many=True)

    return pagintor.get_paginated_response(serialized)


@api_view(["GET"])
@permission_classes([AllowAny])
def get_popular_clan(request):
    clans = get_famous_clans()

    paginator = PopularClanPagination()
    result = paginator.paginate_queryset(clans, many=True)

    serialized = ClansSerializer(result, many=True)

    return paginator.get_paginated_response(serialized)



@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_clan(request):
    pass


'''
Todays task
1. Creating a clan
2. Joining a clan
3. Update clan
4. leave clan
'''

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_clan(request):
    pass


@api_view(["PUT", "PATCH"])
@permission_classes([IsAuthenticated])
def update_clan(request):
    pass


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def join_clan(request):
    pass


@api_view([])
@permission_classes([])
def leave_clan(request):
    pass

