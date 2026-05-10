from rest_framework import generics, status
from rest_framework.response import Response
from apps.users.permissions import IsAdminOrReadOnly
from .models import KnowledgeBase
from .serializers import KnowledgeBaseSerializer
from .tasks import index_document_task


class KnowledgeListView(generics.ListCreateAPIView):
    queryset = KnowledgeBase.objects.all().order_by('-created_at')
    serializer_class = KnowledgeBaseSerializer
    permission_classes = [IsAdminOrReadOnly]

    def perform_create(self, serializer):
        instance = serializer.save()
        # Trigger async indexing
        index_document_task.apply_async(args=[instance.id], queue='default')


class KnowledgeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = KnowledgeBase.objects.all()
    serializer_class = KnowledgeBaseSerializer
    permission_classes = [IsAdminOrReadOnly]

    def perform_destroy(self, instance):
        # Remove from vector DB before deleting
        from apps.rag.services import rag_service
        try:
            rag_service.delete_document(instance.id)
        except Exception:
            pass
        instance.delete()
