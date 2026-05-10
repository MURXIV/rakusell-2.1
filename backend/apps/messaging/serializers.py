from rest_framework import serializers
from .models import Message


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = [
            'id', 'direction', 'message_type', 'content',
            'status', 'is_ai_generated', 'ai_model_used',
            'ai_tokens_used', 'ai_latency_ms', 'created_at',
        ]
