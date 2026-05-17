from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.clients.models import Client
from apps.users.permissions import IsAdminOrReadOnly
from .services import MessageService
from .tasks import send_whatsapp_message


class SendMessageView(APIView):
    """Manually send a message to a client (from admin panel)."""
    permission_classes = [IsAdminOrReadOnly]

    def post(self, request):
        client_id = request.data.get('client_id')
        content = request.data.get('content', '').strip()

        if not client_id or not content:
            return Response({'error': 'client_id and content are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            client = Client.objects.get(id=client_id)
        except Client.DoesNotExist:
            return Response({'error': 'Client not found'}, status=status.HTTP_404_NOT_FOUND)

        message = MessageService.save_outbound(client=client, content=content)
        send_whatsapp_message.apply_async(args=[message.id], queue='messages')

        return Response({'status': 'queued', 'message_id': message.id})
