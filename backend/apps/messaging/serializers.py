from rest_framework import serializers
from .models import Message


class MessageSerializer(serializers.ModelSerializer):
    content = serializers.SerializerMethodField()

    def get_content(self, obj):
        return obj.decrypted_content

    class Meta:
        model = Message
        fields = [
            'id', 'direction', 'message_type', 'content',
            'status', 'is_ai_generated', 'ai_model_used',
            'ai_tokens_used', 'ai_latency_ms', 'created_at',
        ]
