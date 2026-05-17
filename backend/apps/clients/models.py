from django.db import models
from core.encryption import encrypt, decrypt


class Client(models.Model):
    phone = models.CharField(max_length=500, unique=True, db_index=True)  # encrypted, longer field
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

    def save(self, *args, **kwargs):
        if self.phone:
            self.phone = encrypt(self.phone)
        if self.context_summary:
            self.context_summary = encrypt(self.context_summary)
        super().save(*args, **kwargs)

    @property
    def decrypted_phone(self) -> str:
        return decrypt(self.phone)

    @property
    def decrypted_context_summary(self) -> str:
        return decrypt(self.context_summary)

    def __str__(self):
        return f'{self.name or self.decrypted_phone} ({self.chat_id})'
