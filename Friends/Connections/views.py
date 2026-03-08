from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from Connections.models import Friend
from Profiles.models import UserProfile
from Connections.serializer import SendRequestSerializer, RespondRequestSerializer, PendingFriendRequestSerializer, ListFriendsSerializer, PendingSentSerializer
from rest_framework import status
from Connections.services import Friendservices
from Connections.pagination import PendingRequestPagination, ListFriendsPagination, IsPendingRequestPagination


# Create your views here.


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def send_request(request):
    serializer = SendRequestSerializer(
        data=request.data,
        context={"request": request}
    )
    
    serializer.is_valid(raise_exception=True)

    sender = request.user
    receiver = serializer.validated_data["receiver_id"]

    try:
        Friendservices.send_friend_request(sender, receiver)
    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    return Response({"detail": "Friend request sent"}, status=status.HTTP_201_CREATED)



@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def respond_request(request):
    serializer = RespondRequestSerializer(
        data=request.data,
        context = {"request": request}
    )

    serializer.is_valid(raise_exception=True)

    responder = request.user
    connection = serializer.validated_data["connection_id"]
    action = serializer.validated_data["action"]

    try:
        friendship = Friendservices.respond_connection_request(
            responder=responder,
            connection_id=connection,
            action=action
        )
    except ValueError as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    return Response(
        {
            "message": f"Request {action} successfully.",
            "connection_id": friendship.id,
            "status": friendship.status
        },
        status=status.HTTP_200_OK
    )

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_pending_requests(request):
    user = request.user

    
    friends = Friendservices.get_friend_pending_requests(user)

    paginator = PendingRequestPagination()
    result_pages = paginator.paginate_queryset(friends, request)

    serializer = PendingFriendRequestSerializer(result_pages, many=True) # many=True imp as F

    return  paginator.get_paginated_response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_friends(request):
    user = request.user

    friends = Friendservices.get_friends(user)

    paginator = ListFriendsPagination()
    results = paginator.paginate_queryset(friends, request)

    serializer = ListFriendsSerializer(results, many=True)

    return paginator.get_paginated_response(serializer.data)



@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_pending_sent(request):
    user = request.user

    friend_requests = Friendservices.get_pending_sent_requests(user)

    paginator = IsPendingRequestPagination()
    results = paginator.paginate_queryset(friend_requests, request)

    serializer = PendingSentSerializer(results, many=True)

    return paginator.get_paginated_response(serializer.data)