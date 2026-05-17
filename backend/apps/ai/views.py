from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.users.permissions import IsAdmin


class AIStatusView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        return Response({
            'provider': settings.AI_PROVIDER,
            'model': settings.AI_MODEL,
            'max_tokens': settings.AI_MAX_TOKENS,
            'history_limit': settings.AI_HISTORY_LIMIT,
        })
