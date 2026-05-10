import hashlib
import hmac
import logging

from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.logs.services import LogService
from core.throttles import WebhookRateThrottle
from .tasks import process_incoming_webhook

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class WhatsAppWebhookView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_classes = [WebhookRateThrottle]

    def post(self, request, *args, **kwargs):
        try:
            payload = request.data

            if settings.WEBHOOK_SECRET:
                if not self._verify_signature(request):
                    LogService.warning('webhook', 'Webhook signature verification failed', payload={})
                    return Response({'error': 'Invalid signature'}, status=status.HTTP_403_FORBIDDEN)

            type_webhook = payload.get('typeWebhook', '')
            if type_webhook not in ('incomingMessageReceived', 'outgoingMessageStatus'):
                return Response({'status': 'ignored'}, status=status.HTTP_200_OK)

            id_message = payload.get('idMessage', '')
            if not id_message:
                return Response({'status': 'ignored'}, status=status.HTTP_200_OK)

            LogService.info(
                'webhook',
                f'Webhook received: {type_webhook} | id={id_message}',
                payload=payload
            )

            process_incoming_webhook.apply_async(
                args=[payload],
                task_id=f'webhook-{id_message}',
                queue='messages',
                countdown=0,
            )

            return Response({'status': 'queued'}, status=status.HTTP_200_OK)

        except Exception as e:
            logger.exception('Webhook processing error')
            LogService.error('webhook', f'Webhook error: {str(e)}')
            return Response({'status': 'error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _verify_signature(self, request) -> bool:
        signature = request.headers.get('X-Green-Api-Signature', '')
        if not signature:
            return False
        body = request.body
        expected = hmac.new(
            settings.WEBHOOK_SECRET.encode(),
            body,
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(signature, expected)
