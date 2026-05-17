import logging

from celery import shared_task
from django.db import transaction

from apps.clients.services import ClientService
from apps.logs.services import LogService
from apps.messaging.services import MessageService

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
    from django.conf import settings

    sender_data = payload.get('senderData', {})
    message_data = payload.get('messageData', {})
    id_message = payload.get('idMessage', '')

    chat_id = sender_data.get('chatId', '')
    sender_name = sender_data.get('senderName', '')
    chat_name = sender_data.get('chatName', '')

    is_direct = chat_id.endswith('@c.us')
    is_group = chat_id.endswith('@g.us')

    if not is_direct and not is_group:
        logger.info(f'Skipping unsupported chat id: {chat_id}')
        LogService.warning('webhook', f'Skipped unsupported chat id: {chat_id}', payload=payload)
        return
    if is_group and not settings.RESPOND_TO_GROUPS:
        logger.info(f'Skipping group message from {chat_id}; RESPOND_TO_GROUPS=False')
        LogService.warning('webhook', f'Skipped group message: {chat_id}', payload=payload)
        return

    phone = chat_id.replace('@c.us', '').replace('@g.us', '')
    text_message = _extract_text_message(message_data)
    if not text_message:
        logger.info(f'Skipping non-text message from {chat_id}; type={message_data.get("typeMessage", "")}')
        LogService.warning(
            'webhook',
            f'Skipped non-text message from {chat_id}; type={message_data.get("typeMessage", "")}',
            payload=payload,
        )
        return

    with transaction.atomic():
        client = ClientService.get_or_create(
            chat_id=chat_id,
            phone=phone,
            name=chat_name or sender_name,
        )

        message = MessageService.save_inbound(
            client=client,
            content=text_message,
            green_api_message_id=id_message,
        )

        if message is None:
            logger.info(f'Duplicate message ignored: {id_message}')
            return

    if client.is_blocked:
        LogService.info(
            'webhook',
            f'AI auto-reply skipped for blocked client {client.decrypted_phone}',
            client=client,
            payload={'chat_id': chat_id, 'id_message': id_message},
        )
        return

    _schedule_ai_response_debounced(message.chat_id)

    try:
        from asgiref.sync import async_to_sync
        from channels.layers import get_channel_layer

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
            },
        )
    except Exception as ws_err:
        logger.warning(f'WebSocket push failed: {ws_err}')

    LogService.info(
        'message_received',
        f'Message from {client.decrypted_phone}: {text_message[:80]}',
        client=client,
    )


def _extract_text_message(message_data: dict) -> str:
    type_message = message_data.get('typeMessage', '')
    if type_message == 'textMessage':
        return message_data.get('textMessageData', {}).get('textMessage', '').strip()
    if type_message == 'extendedTextMessage':
        return message_data.get('extendedTextMessageData', {}).get('text', '').strip()
    if type_message == 'quotedMessage':
        quoted = message_data.get('quotedMessage', {})
        return (
            quoted.get('textMessage', '')
            or quoted.get('textMessageData', {}).get('textMessage', '')
            or quoted.get('extendedTextMessageData', {}).get('text', '')
        ).strip()
    return (
        message_data.get('textMessageData', {}).get('textMessage', '')
        or message_data.get('extendedTextMessageData', {}).get('text', '')
        or ''
    ).strip()


def _schedule_ai_response_debounced(chat_id: int):
    from django.conf import settings
    import redis as redis_lib

    r = redis_lib.from_url(settings.REDIS_URL)
    redis_key = f'pending_ai_task:{chat_id}'
    debounce_seconds = settings.MESSAGE_GROUPING_SECONDS

    from apps.ai.tasks import generate_ai_response_for_chat

    result = generate_ai_response_for_chat.apply_async(
        args=[chat_id],
        queue='ai',
        countdown=debounce_seconds,
    )

    r.setex(redis_key, max(debounce_seconds * 12, 300), result.id)


def _handle_outgoing_status(payload: dict):
    id_message = payload.get('idMessage', '')
    status_str = payload.get('status', '')

    from apps.messaging.models import Message

    Message.objects.filter(green_api_message_id=id_message).update(
        status=status_str if status_str in ('sent', 'delivered', 'read', 'failed') else 'sent'
    )
