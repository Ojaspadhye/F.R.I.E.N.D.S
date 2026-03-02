from cassandra.cqlengine import columns
from django_cassandra_engine.models import DjangoCassandraModel
import uuid
from django.db import models
from datetime import datetime


# Create your models here.

'''
I tried to combine them. Then i asked chatgpt it suggested to do other wise and it kind of made sense
    A) Data duplication (denormalization risk)
        Every message repeats the conversation participants list.
        In a group chat with 50 participants and thousands of messages, that’s huge duplication.

    B) Updating conversation info becomes hard
        Say you add/remove participants, or rename a conversation:
        You now need to update every row in the table, which is expensive in Cassandra.

    C) And i have watch video where they stronly suggest keeping the metadata seperate from the data as it makes life simple
'''


class ContextMessages(DjangoCassandraModel):
    context_id = columns.UUID(primary_key=True)
    type = columns.Text(max_length=10)  # Where message is sent in friends or the clans
    participants = columns.List(value_type=columns.UUID)
    created_at = columns.DateTime(default=datetime.utcnow)

    class Meta:
        get_pk_field = 'context_id'


class MessagesManager(models.Manager):
    def send_message(self, context_id, sender_id, content):
        message = self.model(
            context_id=context_id,
            content=content,
            sender_id=sender_id
        )

        message.save()
        return message
    
    def get_messages(self, context_id, limit=50):
        return self.filter(context_id=context_id).order_by("-message_id")[:limit]


class Messages(DjangoCassandraModel):
    context_id = columns.UUID(primary_key=True)  # Partition key
    message_id = columns.TimeUUID(primary_key=True, default=uuid.uuid1)  # Clustering key
    content = columns.Text()
    sender_id = columns.UUID()
    created_at = columns.DateTime(default=datetime.utcnow)

    object = MessagesManager()

    class Meta:
        get_pk_field = 'message_id'