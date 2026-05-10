from django.db import models
from apps.users.models import User


class Prompt(models.Model):

    class Scenario(models.TextChoices):
        SALES = 'sales', 'Sales'
        SUPPORT = 'support', 'Support'
        GENERAL = 'general', 'General'

    name = models.CharField(max_length=255)
    scenario = models.CharField(max_length=20, choices=Scenario.choices, default=Scenario.GENERAL)
    system_prompt = models.TextField()
    is_active = models.BooleanField(default=False)
    is_ab_test = models.BooleanField(default=False)
    ab_weight = models.FloatField(default=1.0)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='prompts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'prompts'
        verbose_name = 'Prompt'
        verbose_name_plural = 'Prompts'

    def __str__(self):
        return f'{self.name} ({self.scenario}) {"[ACTIVE]" if self.is_active else ""}'

    def save(self, *args, **kwargs):
        if self.is_active and not self.is_ab_test:
            Prompt.objects.filter(
                scenario=self.scenario,
                is_active=True,
                is_ab_test=False
            ).exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)
