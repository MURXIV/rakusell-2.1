from rest_framework import serializers
from .models import Client


class ClientSerializer(serializers.ModelSerializer):
    phone = serializers.SerializerMethodField()

    def get_phone(self, obj):
        return obj.decrypted_phone

    class Meta:
        model = Client
        fields = ['id', 'phone', 'name', 'chat_id', 'tags', 'last_seen', 'is_blocked', 'created_at']


class ClientDetailSerializer(serializers.ModelSerializer):
    phone = serializers.SerializerMethodField()
    context_summary = serializers.SerializerMethodField()

    def get_phone(self, obj):
        return obj.decrypted_phone

    def get_context_summary(self, obj):
        return obj.decrypted_context_summary

    class Meta:
        model = Client
        fields = '__all__'
