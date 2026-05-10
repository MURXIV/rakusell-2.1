import logging

from celery import shared_task

from apps.logs.services import LogService
from .models import Message
from .services import green_api

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    queue='messages',
    max_retries=5,
    default_retry_delay=10,
    acks_late=True,
)
def send_whatsapp_message(self, message_id: int):
    try:
        message = Message.objects.select_related('chat__client').get(id=message_id)
        client = message.chat.client

        result = green_api.send_message(
            chat_id=client.chat_id,
            message=message.content,
        )

        if result['success']:
            message.green_api_message_id = result.get('id_message', '')
            message.status = Message.Status.SENT
            message.save(update_fields=['green_api_message_id', 'status'])

            LogService.info(
                'message_sent',
                f'Sent to {client.phone}: {message.content[:80]}',
                client=client,
                payload={'latency_ms': result.get('latency_ms', 0)},
            )
        else:
            raise Exception(result.get('error', 'Unknown error'))

    except Message.DoesNotExist:
        logger.error(f'Message {message_id} not found')
    except Exception as exc:
        logger.exception(f'Failed to send message {message_id}: {exc}')
        if self.request.retries >= self.max_retries:
            Message.objects.filter(id=message_id).update(status=Message.Status.FAILED)
            LogService.error('api_error', f'Message {message_id} failed after {self.max_retries} retries')
        raise self.retry(exc=exc, countdown=2 ** self.request.retries * 5)
