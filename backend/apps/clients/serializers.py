from rest_framework import serializers
from .models import Client


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['id', 'phone', 'name', 'chat_id', 'tags', 'last_seen', 'is_blocked', 'created_at']


class ClientDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'
