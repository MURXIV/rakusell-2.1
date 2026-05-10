from rest_framework import serializers
from .models import Chat
from apps.clients.serializers import ClientSerializer


class ChatSerializer(serializers.ModelSerializer):
    client = ClientSerializer(read_only=True)

    class Meta:
        model = Chat
        fields = ['id', 'client', 'status', 'last_message_at', 'unread_count', 'created_at']
