from django.db import models
from apps.clients.models import Client


class Log(models.Model):
    """System-wide logging for API calls, AI requests, and webhook events."""

    class LogType(models.TextChoices):
        WEBHOOK = 'webhook', 'Webhook Event'
        AI_REQUEST = 'ai_request', 'AI Request'
        AI_ERROR = 'ai_error', 'AI Error'
        API_ERROR = 'api_error', 'API Error'
        MESSAGE_SENT = 'message_sent', 'Message Sent'
        MESSAGE_RECEIVED = 'message_received', 'Message Received'
        SYSTEM = 'system', 'System'

    class Level(models.TextChoices):
        INFO = 'info', 'Info'
        WARNING = 'warning', 'Warning'
        ERROR = 'error', 'Error'
        CRITICAL = 'critical', 'Critical'

    log_type = models.CharField(max_length=30, choices=LogType.choices, db_index=True)
    level = models.CharField(max_length=10, choices=Level.choices, default=Level.INFO)
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True, related_name='logs')

    message = models.TextField()
    payload = models.JSONField(default=dict, blank=True)  # Request/response data
    error_traceback = models.TextField(blank=True)

    # Performance tracking
    latency_ms = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'logs'
        verbose_name = 'Log'
        verbose_name_plural = 'Logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['log_type', 'level', 'created_at']),
        ]

    def __str__(self):
        return f'[{self.level.upper()}] {self.log_type}: {self.message[:80]}'
