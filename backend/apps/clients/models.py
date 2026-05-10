from django.db import models


class Client(models.Model):
    phone = models.CharField(max_length=30, unique=True, db_index=True)
    name = models.CharField(max_length=255, blank=True)
    chat_id = models.CharField(max_length=50, unique=True, db_index=True)
    preferences = models.JSONField(default=dict, blank=True)
    context_summary = models.TextField(blank=True)
    tags = models.JSONField(default=list, blank=True)
    is_blocked = models.BooleanField(default=False)
    last_seen = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'clients'
        verbose_name = 'Client'
        verbose_name_plural = 'Clients'

    def __str__(self):
        return f'{self.name or self.phone} ({self.chat_id})'
