
from django.core.management.base import BaseCommand
from cassandra.cqlengine import connection
from cassandra.cqlengine.management import sync_table
from Messaging.models import ContextMessages, Messages

class Command(BaseCommand):
    help = 'Sync_Cassandra'

    def handle(self, *args, **kwargs):
        connection.setup(['127.0.0.1'], "messaging", protocol_version=3)
        sync_table(ContextMessages)
        sync_table(Messages)
        self.stdout.write(self.style.SUCCESS('Cassandra tables synced!'))