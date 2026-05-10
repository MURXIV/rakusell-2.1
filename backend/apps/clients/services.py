from django.utils import timezone
from .models import Client


class ClientService:

    @staticmethod
    def get_or_create(chat_id: str, phone: str, name: str = '') -> Client:
        """Get or create a client by chat_id. Updates name and last_seen."""
        client, created = Client.objects.get_or_create(
            chat_id=chat_id,
            defaults={'phone': phone, 'name': name},
        )
        if not created:
            update_fields = ['last_seen']
            client.last_seen = timezone.now()
            if name and not client.name:
                client.name = name
                update_fields.append('name')
            client.save(update_fields=update_fields)
        return client
