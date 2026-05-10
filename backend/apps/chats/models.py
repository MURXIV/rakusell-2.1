from django.db import models
from apps.clients.models import Client


class Chat(models.Model):
    """Represents a WhatsApp conversation thread with a client."""

    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        CLOSED = 'closed', 'Closed'
        PENDING = 'pending', 'Pending'

    client = models.OneToOneField(Client, on_delete=models.CASCADE, related_name='chat')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    last_message_at = models.DateTimeField(null=True, blank=True)
    unread_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'chats'
        verbose_name = 'Chat'
        verbose_name_plural = 'Chats'
        ordering = ['-last_message_at']

    def __str__(self):
        return f'Chat with {self.client}'
