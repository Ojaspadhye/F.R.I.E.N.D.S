from django.core.mail import send_mail
from Connections.models import Friend, FriendMeta
from Connections.notifications import send_friends_notification_async
from django.utils import timezone


class Friendservices:

    @staticmethod
    def send_friend_request(sender, reciver):
        friendship = Friend.objects.send_request(sender, reciver)

        send_friends_notification_async(
            user=reciver.username,
            message=f"New Connection Request: {sender.username}"
        )

    @staticmethod
    def respond_connection_request(responder, connection_id, action):
        try:
            friendship = Friend.objects.get(id=connection_id)
        except Friend.DoesNotExist:
            raise ValueError("Connection does not exist.")

        friendship = Friend.objects.respond(
            friendship,
            responder,
            action
        )

        if action == "accepted":

            sender = friendship.sender
            send_friends_notification_async(
                sender.id,
                f"{responder.username} accepted your request"
            )

        return friendship
    
    @staticmethod
    def get_friend_pending_requests(user):
        return Friend.objects.received_ispending(user)
    
    @staticmethod
    def get_friends(user):
        return Friend.objects.get_friends(user)
    
    @staticmethod
    def get_pending_sent_requests(user):
        return Friend.objects.sent_ispending(user)
    


