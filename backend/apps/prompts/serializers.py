from rest_framework import serializers
from .models import Prompt


class PromptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prompt
        fields = '__all__'
        read_only_fields = ['created_by', 'created_at', 'updated_at']
