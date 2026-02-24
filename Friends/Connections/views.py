from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from Connections.models import Friend
from Profiles.models import UserProfile
from rest_framework import serializers


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
        ]


class FriendSerializer(serializers.ModelSerializer):
    sender = UserProfileSerializer(read_only=True)
    user1 = UserProfileSerializer(read_only=True)
    user2 = UserProfileSerializer(read_only=True)
    class Meta:
        model = Friend
        fields = [
            "id",
            "user1",
            "user2",
            "sender",
            "status",
            "created_at"
        ]

# Create your views here.


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def send_request(request):
    reciver_id = request.data.get("reciverId")

    if not reciver_id:
        return Response(
            {"error": "ReciverId not mentioned"},
            status=400
        )
    
    try:
        reciver = UserProfile.objects.get(id=reciver_id)
    except UserProfile.DoesNotExist:
        return Response(
            {"error": "Reciver dose not exiset"},
            status=404
        )
    
    try:
        relation = Friend.objects.send_request(
            sender=request.user,
            receiver=reciver
        )
    except ValueError as e:
        return Response(
            {"error": str(e)},
            status=400
        )
    
    return Response(
        {"message": "Request sent successfully"},
        status=201
    )



@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def respond_request(request):
    request_id = request.data.get("requestid")
    action = request.data.get("action")

    if not request_id or not action:
        return Response({"error": "Invalid data"}, status=400)

    try:
        relation = Friend.objects.get(id=request_id)
    except Friend.DoesNotExist:
        return Response({"error": "Request not found"}, status=404)

    try:
        updated = Friend.objects.responding_request(
            relation,
            request.user,
            action
        )
    except ValueError as e:
        return Response({"error": str(e)}, status=400)

    serializer = FriendSerializer(updated)
    return Response(serializer.data, status=200)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_friends(request):
    user = request.user.id

    friends = Friend.objects.get_friends(user)
    serializer = UserProfileSerializer(friends, many=True)

    return Response(serializer.data, status=200)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_pending_recived(request):
    relations = Friend.objects.received_ispending(
        request.user.id
    )

    serializer = FriendSerializer(relations, many=True)

    return Response(serializer.data, status=200)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_pending_sent(request):
    relations = Friend.objects.sent_ispending(
        request.user.profile
    )

    serializer = FriendSerializer(relations, many=True)

    return Response(serializer.data, status=200)

