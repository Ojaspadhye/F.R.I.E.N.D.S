from rest_framework import serializers
from Connections.models import Friend, FriendMeta
from Profiles.models import UserProfile


class SendRequestSerializer(serializers.Serializer):
    receiver_id = serializers.IntegerField()

    def validate_receiver_id(self, value):
        try:
            receiver = UserProfile.objects.get(id=value)
        except UserProfile.DoesNotExist:
            raise serializers.ValidationError("Receiver does not exist")

        return receiver

    def validate_sender_reciver_relation(self, data):
        sender = self.context["request"].user
        receiver = data["receiver_id"]

        if sender == receiver:
            raise serializers.ValidationError(
                "You can't send request to yourself"
            )

        if sender.id < receiver.id:
            user1, user2 = sender, receiver
        else:
            user1, user2 = receiver, sender

        if Friend.objects.filter(user1=user1, user2=user2).exists():
            raise serializers.ValidationError(
                "Friendship already exists"
            )

        return data


class RespondRequestSerializer(serializers.Serializer):
    connection_id = serializers.IntegerField()
    action = serializers.ChoiceField(
        choices=[
        ('accepted', 'accepted'),
        ('blocked', 'blocked'),
        ('rejected', 'rejected'),
        ]
    )

    def validate_connection_id(self, connction_id):
        try:
            connection = Friend.objects.get(id=connction_id)
        except Friend.DoesNotExist:
            raise serializers.ValidationError("Connection doesnot exisit")

    def validate_connections_status(self, data):
        user = self.context["request"].user.userprofile
        connection = data["connection_id"]

        if user != connection.user1 and user != connection.user2:
            raise serializers.ValidationError("You are not part of this connection")

        return data


