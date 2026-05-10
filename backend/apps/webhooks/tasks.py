import logging

from celery import shared_task
from django.db import transaction

from apps.clients.services import ClientService
from apps.messaging.services import MessageService
from apps.ai.tasks import generate_ai_response
from apps.logs.services import LogService

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    queue='messages',
    max_retries=3,
    default_retry_delay=5,
    acks_late=True,
    reject_on_worker_lost=True,
)
def process_incoming_webhook(self, payload: dict):
    try:
        type_webhook = payload.get('typeWebhook', '')

        if type_webhook == 'incomingMessageReceived':
            _handle_incoming_message(payload)
        elif type_webhook == 'outgoingMessageStatus':
            _handle_outgoing_status(payload)

    except Exception as exc:
        logger.exception(f'Error processing webhook: {exc}')
        LogService.error('webhook', f'Task error: {str(exc)}', payload=payload)
        raise self.retry(exc=exc)


def _handle_incoming_message(payload: dict):
    sender_data = payload.get('senderData', {})
    message_data = payload.get('messageData', {})
    id_message = payload.get('idMessage', '')

    chat_id = sender_data.get('chatId', '')
    sender_name = sender_data.get('senderName', '')
    phone = chat_id.replace('@c.us', '').replace('@g.us', '')

    text_message = message_data.get('textMessageData', {}).get('textMessage', '')
    if not text_message:
        logger.info(f'Skipping non-text message from {chat_id}')
        return

    with transaction.atomic():
        client = ClientService.get_or_create(
            chat_id=chat_id,
            phone=phone,
            name=sender_name,
        )

        message = MessageService.save_inbound(
            client=client,
            content=text_message,
            green_api_message_id=id_message,
        )

        if message is None:
            logger.info(f'Duplicate message ignored: {id_message}')
            return

    generate_ai_response.apply_async(
        args=[message.id],
        queue='ai',
    )

    # Push incoming message to WebSocket
    try:
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'chat_{message.chat_id}',
            {
                'type': 'chat_message',
                'message': {
                    'id': message.id,
                    'content': text_message,
                    'direction': 'inbound',
                    'created_at': message.created_at.isoformat(),
                    'is_ai_generated': False,
                },
            }
        )
    except Exception as ws_err:
        logger.warning(f'WebSocket push failed: {ws_err}')

    LogService.info(
        'message_received',
        f'Message from {phone}: {text_message[:80]}',
        client=client,
    )


def _handle_outgoing_status(payload: dict):
    id_message = payload.get('idMessage', '')
    status_str = payload.get('status', '')

    from apps.messaging.models import Message
    Message.objects.filter(green_api_message_id=id_message).update(
        status=status_str if status_str in ('sent', 'delivered', 'read', 'failed') else 'sent'
    )
