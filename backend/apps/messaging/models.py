from django.db import models
from apps.chats.models import Chat


class Message(models.Model):

    class Direction(models.TextChoices):
        INBOUND = 'inbound', 'Inbound'
        OUTBOUND = 'outbound', 'Outbound'

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        SENT = 'sent', 'Sent'
        DELIVERED = 'delivered', 'Delivered'
        READ = 'read', 'Read'
        FAILED = 'failed', 'Failed'

    class MessageType(models.TextChoices):
        TEXT = 'text', 'Text'
        IMAGE = 'image', 'Image'
        DOCUMENT = 'document', 'Document'
        AUDIO = 'audio', 'Audio'
        VIDEO = 'video', 'Video'

    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')
    direction = models.CharField(max_length=10, choices=Direction.choices)
    message_type = models.CharField(max_length=20, choices=MessageType.choices, default=MessageType.TEXT)
    content = models.TextField()
    media_url = models.URLField(blank=True)
    green_api_message_id = models.CharField(max_length=100, unique=True, null=True, blank=True, db_index=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    is_ai_generated = models.BooleanField(default=False)
    ai_model_used = models.CharField(max_length=50, blank=True)
    ai_tokens_used = models.PositiveIntegerField(default=0)
    ai_latency_ms = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'messages'
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['chat', 'created_at']),
            models.Index(fields=['direction', 'status']),
        ]

    def __str__(self):
        return f'[{self.direction}] {self.content[:50]}'
