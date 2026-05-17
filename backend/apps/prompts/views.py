from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.users.permissions import IsAdminOrReadOnly
from .models import Prompt
from .serializers import PromptSerializer
from .services import PromptService


class PromptListView(generics.ListCreateAPIView):
    queryset = Prompt.objects.all().order_by('-created_at')
    serializer_class = PromptSerializer
    permission_classes = [IsAdminOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class PromptDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Prompt.objects.all()
    serializer_class = PromptSerializer
    permission_classes = [IsAdminOrReadOnly]


class ActivePromptView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        scenario = request.query_params.get('scenario', 'general')
        text = PromptService.get_active_prompt(scenario)
        return Response({'scenario': scenario, 'system_prompt': text})
