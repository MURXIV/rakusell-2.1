from rest_framework import serializers
from .models import KnowledgeBase, Embedding


class EmbeddingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Embedding
        fields = ['id', 'chunk_index', 'chunk_text', 'chroma_id', 'token_count', 'created_at']


class KnowledgeBaseSerializer(serializers.ModelSerializer):
    embeddings = EmbeddingSerializer(many=True, read_only=True)

    class Meta:
        model = KnowledgeBase
        fields = '__all__'
        read_only_fields = ['is_indexed', 'chunk_count', 'created_at', 'updated_at']
