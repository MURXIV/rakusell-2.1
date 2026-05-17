import logging
import threading

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

        from django.conf import settings
        system_prompt = PromptService.get_active_prompt(settings.AI_PROMPT_SCENARIO)
        rag_context = _get_rag_context(message.decrypted_content, client)
        client_context = _build_client_context(client)

        from apps.ai.services import ai_service
        result = ai_service.generate_response(
            system_prompt=system_prompt,
            history=history,
            user_message=message.decrypted_content,
            context=rag_context,
            client_context=client_context,
        )

        outbound = _save_ai_outbound(client, result)
        send_whatsapp_message.apply_async(args=[outbound.id], queue='messages')
        _push_ws_message(chat.id, outbound, result['content'])

    except Message.DoesNotExist:
        logger.error(f'Message {message_id} not found for AI processing')
    except Exception as exc:
        logger.exception(f'AI generation failed for message {message_id}: {exc}')
        LogService.error('ai_error', f'AI task failed: {str(exc)}')
        raise self.retry(exc=exc)


@shared_task(
    bind=True,
    queue='ai',
    max_retries=3,
    default_retry_delay=15,
    acks_late=True,
    time_limit=60,
    soft_time_limit=45,
)
def generate_ai_response_for_chat(self, chat_id: int):
    """
    Responds to all pending inbound messages in one chat after a debounce delay.
    This prevents one WhatsApp burst from becoming many bot replies.
    """
    from apps.chats.models import Chat

    task_id = self.request.id
    try:
        if not _is_latest_grouped_task(chat_id, task_id):
            logger.info(f'Skipping stale grouped AI task for chat {chat_id}')
            return

        # Acquire processing lock — prevent concurrent duplicate execution
        if not _acquire_processing_lock(chat_id, task_id, ttl=90):
            logger.info(f'Another AI task already processing chat {chat_id}, skipping {task_id}')
            return

        try:
            chat = Chat.objects.select_related('client').get(id=chat_id)
            client = chat.client
            pending_messages = _pending_inbound_messages(chat)

            if not pending_messages:
                _clear_grouped_task_marker(chat_id, task_id)
                return

            combined = '\n'.join(m.decrypted_content for m in pending_messages)
            history = _build_history(chat, exclude_ids=[m.id for m in pending_messages])

            from django.conf import settings
            system_prompt = PromptService.get_active_prompt(settings.AI_PROMPT_SCENARIO)
            rag_context = _get_rag_context(combined, client)
            client_context = _build_client_context(client)

            # Show "typing..." indicator while AI generates
            stop_typing = threading.Event()
            typing_thread = threading.Thread(
                target=_typing_loop,
                args=(client.chat_id, stop_typing, 4.0),
                daemon=True,
            )
            typing_thread.start()

            from apps.ai.services import ai_service
            try:
                result = ai_service.generate_response(
                    system_prompt=system_prompt,
                    history=history,
                    user_message=combined,
                    context=rag_context,
                    client_context=client_context,
                )
            finally:
                stop_typing.set()
                typing_thread.join(timeout=5)

            LogService.info(
                'ai_request',
                f'AI grouped response for {client.decrypted_phone} ({len(pending_messages)} msgs) | tokens={result["tokens"]}',
                client=client,
                payload={
                    'model': result['model'],
                    'tokens': result['tokens'],
                    'latency_ms': result['latency_ms'],
                },
            )

            outbound = _save_ai_outbound(client, result)
            send_whatsapp_message.apply_async(args=[outbound.id], queue='messages')
            _clear_grouped_task_marker(chat_id, task_id)
            _push_ws_message(chat.id, outbound, result['content'])

        finally:
            _release_processing_lock(chat_id, task_id)

    except Exception as exc:
        logger.exception(f'Grouped AI generation failed for chat {chat_id}: {exc}')
        LogService.error('ai_error', f'Grouped AI task failed: {str(exc)}')
        raise self.retry(exc=exc)


def _typing_loop(chat_id_str: str, stop_event: threading.Event, interval: float = 4.0):
    """Send 'typing...' indicator every `interval` seconds until stop_event is set."""
    from apps.messaging.services import green_api
    while not stop_event.is_set():
        green_api.send_typing(chat_id_str)
        stop_event.wait(timeout=interval)


def _pending_inbound_messages(chat):
    last_outbound = Message.objects.filter(
        chat=chat,
        direction=Message.Direction.OUTBOUND,
        is_ai_generated=True,
    ).order_by('-created_at').first()

    pending_qs = Message.objects.filter(
        chat=chat,
        direction=Message.Direction.INBOUND,
    )
    if last_outbound:
        pending_qs = pending_qs.filter(created_at__gt=last_outbound.created_at)

    return list(pending_qs.order_by('created_at'))


def _save_ai_outbound(client, result: dict) -> Message:
    return MessageService.save_outbound(
        client=client,
        content=result['content'],
        ai_model=result['model'],
        tokens=result['tokens'],
        latency_ms=result['latency_ms'],
    )


def _get_rag_context(query: str, client) -> str:
    try:
        from apps.rag.services import rag_service
        return rag_service.search(query=query, client_id=client.id)
    except Exception as exc:
        logger.warning(f'RAG search failed: {exc}')
        return ''


def _build_client_context(client) -> str:
    parts = [_build_runtime_context()]
    if client.context_summary:
        parts.append(f'Контекст клиента: {client.decrypted_context_summary}')
    if client.preferences:
        prefs = ', '.join(f'{k}: {v}' for k, v in client.preferences.items())
        parts.append(f'Предпочтения: {prefs}')
    if client.tags:
        parts.append(f'Теги: {", ".join(client.tags)}')
    if client.name:
        parts.append(f'Имя клиента: {client.name}')
    return '\n'.join(parts)


def _build_runtime_context() -> str:
    from datetime import datetime
    from zoneinfo import ZoneInfo
    from django.conf import settings

    tz_name = getattr(settings, 'BOT_TIME_ZONE', 'Asia/Qyzylorda')
    now = datetime.now(ZoneInfo(tz_name))
    hour = now.hour

    if 5 <= hour < 12:
        greeting_period = 'утро'
        allowed_greeting = 'Доброе утро'
    elif 12 <= hour < 18:
        greeting_period = 'день'
        allowed_greeting = 'Добрый день'
    elif 18 <= hour < 23:
        greeting_period = 'вечер'
        allowed_greeting = 'Добрый вечер'
    else:
        greeting_period = 'ночь'
        allowed_greeting = 'Здравствуйте'

    return (
        'Текущий локальный контекст для ответа:\n'
        f'- Часовой пояс: {tz_name}\n'
        f'- Сейчас: {now:%Y-%m-%d %H:%M}\n'
        f'- Период суток: {greeting_period}\n'
        f'- Если нужно приветствие, используй: "{allowed_greeting}".\n'
        '- Не говори "доброй ночи", если период суток не ночь. '
        'Если сомневаешься, используй нейтральное "Здравствуйте".'
    )


def _pending_grouped_task_key(chat_id: int) -> str:
    return f'pending_ai_task:{chat_id}'


def _is_latest_grouped_task(chat_id: int, task_id: str) -> bool:
    from django.conf import settings
    import redis as redis_lib

    r = redis_lib.from_url(settings.REDIS_URL)
    latest_task_id = r.get(_pending_grouped_task_key(chat_id))
    if latest_task_id is None:
        # Key was already cleared by a previous task — skip to avoid duplicate
        logger.info(f'Grouped AI marker already cleared for chat {chat_id}, skipping task {task_id}')
        return False
    return latest_task_id.decode() == task_id


def _clear_grouped_task_marker(chat_id: int, task_id: str):
    from django.conf import settings
    import redis as redis_lib

    r = redis_lib.from_url(settings.REDIS_URL)
    key = _pending_grouped_task_key(chat_id)
    latest_task_id = r.get(key)
    if latest_task_id is None or latest_task_id.decode() == task_id:
        r.delete(key)


def _processing_lock_key(chat_id: int) -> str:
    return f'ai_processing_lock:{chat_id}'


def _acquire_processing_lock(chat_id: int, task_id: str, ttl: int = 90) -> bool:
    """Distributed lock: only one AI task may process per chat at a time."""
    from django.conf import settings
    import redis as redis_lib

    r = redis_lib.from_url(settings.REDIS_URL)
    key = _processing_lock_key(chat_id)
    # SET NX EX — atomic acquire only if not held
    acquired = r.set(key, task_id, nx=True, ex=ttl)
    return bool(acquired)


def _release_processing_lock(chat_id: int, task_id: str):
    from django.conf import settings
    import redis as redis_lib

    r = redis_lib.from_url(settings.REDIS_URL)
    key = _processing_lock_key(chat_id)
    current = r.get(key)
    if current and current.decode() == task_id:
        r.delete(key)


def _build_history(chat, exclude_id: int = None, exclude_ids: list | None = None) -> list[dict]:
    from django.conf import settings
    limit = settings.AI_HISTORY_LIMIT

    qs = Message.objects.filter(chat=chat)
    if exclude_ids:
        qs = qs.exclude(id__in=exclude_ids)
    elif exclude_id:
        qs = qs.exclude(id=exclude_id)

    messages = qs.order_by('-created_at')[:limit]

    history = []
    for msg in reversed(messages):
        role = 'user' if msg.direction == Message.Direction.INBOUND else 'assistant'
        history.append({'role': role, 'content': msg.decrypted_content})

    return history


def _push_ws_message(chat_id: int, message: Message, content: str):
    try:
        from asgiref.sync import async_to_sync
        from channels.layers import get_channel_layer

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'chat_{chat_id}',
            {
                'type': 'chat_message',
                'message': {
                    'id': message.id,
                    'content': content,
                    'direction': 'outbound',
                    'created_at': message.created_at.isoformat(),
                    'is_ai_generated': True,
                },
            },
        )
    except Exception as ws_err:
        logger.warning(f'WebSocket push failed: {ws_err}')
