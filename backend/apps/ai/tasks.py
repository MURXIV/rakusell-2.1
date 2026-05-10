import logging

from celery import shared_task

from apps.logs.services import LogService
from apps.messaging.models import Message
from apps.messaging.services import MessageService
from apps.messaging.tasks import send_whatsapp_message
from apps.prompts.services import PromptService

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    queue='ai',
    max_retries=3,
    default_retry_delay=15,
    acks_late=True,
    time_limit=60,
    soft_time_limit=45,
)
def generate_ai_response(self, message_id: int):
    try:
        message = Message.objects.select_related('chat__client').get(id=message_id)

        client = message.chat.client
        chat = message.chat

        history = _build_history(chat, exclude_id=message_id)
        system_prompt = PromptService.get_active_prompt()
        rag_context = _get_rag_context(message.content, client)
        client_context = _build_client_context(client)

        from apps.ai.services import ai_service
        result = ai_service.generate_response(
            system_prompt=system_prompt,
            history=history,
            user_message=message.content,
            context=rag_context,
            client_context=client_context,
        )

        ai_content = result['content']
        tokens = result['tokens']
        latency_ms = result['latency_ms']
        model = result['model']

        LogService.info(
            'ai_request',
            f'AI response for {client.phone} | tokens={tokens} | latency={latency_ms}ms',
            client=client,
            payload={
                'model': model,
                'tokens': tokens,
                'latency_ms': latency_ms,
                'prompt_length': len(system_prompt),
            },
        )

        outbound = MessageService.save_outbound(
            client=client,
            content=ai_content,
            ai_model=model,
            tokens=tokens,
            latency_ms=latency_ms,
        )

        send_whatsapp_message.apply_async(
            args=[outbound.id],
            queue='messages',
        )

        # Push real-time WebSocket notification
        try:
            from channels.layers import get_channel_layer
            from asgiref.sync import async_to_sync
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'chat_{chat.id}',
                {
                    'type': 'chat_message',
                    'message': {
                        'id': outbound.id,
                        'content': ai_content,
                        'direction': 'outbound',
                        'created_at': outbound.created_at.isoformat(),
                        'is_ai_generated': True,
                    },
                }
            )
        except Exception as ws_err:
            logger.warning(f'WebSocket push failed: {ws_err}')

    except Message.DoesNotExist:
        logger.error(f'Message {message_id} not found for AI processing')
    except Exception as exc:
        logger.exception(f'AI generation failed for message {message_id}: {exc}')
        LogService.error('ai_error', f'AI task failed: {str(exc)}')
        raise self.retry(exc=exc)


def _build_history(chat, exclude_id: int) -> list[dict]:
    from django.conf import settings
    limit = settings.AI_HISTORY_LIMIT

    messages = Message.objects.filter(
        chat=chat
    ).exclude(
        id=exclude_id
    ).order_by('-created_at')[:limit]

    history = []
    for msg in reversed(messages):
        role = 'user' if msg.direction == Message.Direction.INBOUND else 'assistant'
        history.append({'role': role, 'content': msg.content})

    return history


def _get_rag_context(query: str, client) -> str:
    try:
        from apps.rag.services import rag_service
        return rag_service.search(query=query, client_id=client.id)
    except Exception:
        return ''


def _build_client_context(client) -> str:
    parts = []
    if client.context_summary:
        parts.append(f'Контекст клиента: {client.context_summary}')
    if client.preferences:
        prefs = ', '.join(f'{k}: {v}' for k, v in client.preferences.items())
        parts.append(f'Предпочтения: {prefs}')
    if client.tags:
        parts.append(f'Теги: {", ".join(client.tags)}')
    if client.name:
        parts.append(f'Имя клиента: {client.name}')
    return '\n'.join(parts)
