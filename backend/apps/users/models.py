from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Admin/Manager users of the system."""

    class Role(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        MANAGER = 'manager', 'Manager'

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.MANAGER)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f'{self.username} ({self.role})'

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN
