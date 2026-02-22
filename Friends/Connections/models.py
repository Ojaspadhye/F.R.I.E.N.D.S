from django.db import models

# Create your models here.
'''
The reson for keeping the user1 user2 is to keep them in a proper order(ascending), and keep the data of who sent the request we have the another sender column in the table.

Let sender have id == 1 and the reciver id == 2
now when the relation is setup id 1 will be put into user1 and the id 2 will be put in the user 2
and because the sender == id1 it 1 will be put in the sender

now if id 2 tries sending the request to id 1 
it will much easy to flag it down cuz we would just check id 2 in the user2 and id1 un user1


otherwise there might be a chase where redundante requests could be made


This is what i done either this works or i am fucking stupid
'''




class FriendManager():
    def send_request(self, sender, reciver): # To send a request
        if sender == reciver:
            raise ValueError("You cant sent request to yourself")
        
        user1, user2 = sorted([sender, reciver], key=lambda x: x.id)

        isconnections = self.filter(user1=user1, user2=user2).first()
        if isconnections:
            if isconnections.status == 'Blocked':
                raise ValueError("The relation is Blocked")
            
            elif isconnections.status == 'Pending':
                raise ValueError("The request alredy pending")
            
            elif isconnections.status == 'Accepted':
                raise ValueError('Friendship alredy established')
            
            elif isconnections.status == 'Regected':
                isconnections.sender = sender
                isconnections.status = 'Pending'
                isconnections.save()
                return isconnections
            

        return self.create(user1=user1, user2=user2, sender=sender, status='pending')



    def responding_request(self, status_choice, user): # To accept block regect etc
        pass

    def get_friends(self, user): # To get friends that have accepted and user has accepted
        pass

    def sent_ispending(self, user): # To get the pending requests sent by user
        pass

    def recived_ispending(self, user): # To get recived requests sent to user
        pass


class Friend(models.Model):
    user1 = models.ForeignKey( # This is userid1 < userid2 so that it prevents
        'Profiles.UserProfile',
        on_delete=models.CASCADE,
        related_name='user1'
    )

    user2 = models.ForeignKey(
        'Profiles.UserProfile',
        on_delete=models.CASCADE,
        related_name='user2'
    )

    sender = models.ForeignKey(
        'Profiles.UserProfile',
        on_delete=models.CASCADE,
        related_name='sender'
    )

    STATUS_CHOICES = (
        ('Pending', 'pending'), # This is the default on creation
        ('Accepted', 'accepted'),
        ('Blocked', 'blocked'), # If one blocks No Repeted Requests can be made
        ('Regected', 'regected') # Repeted request can be made 
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = FriendManager()


    class Meta:
        constraints = [

        ]


