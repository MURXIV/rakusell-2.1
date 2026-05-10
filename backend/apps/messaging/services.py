import logging
import time
from typing import Optional

import httpx
from django.conf import settings

from apps.clients.models import Client
from apps.chats.models import Chat
from .models import Message

logger = logging.getLogger(__name__)


class MessageService:

    @staticmethod
    def save_inbound(client: Client, content: str, green_api_message_id: str) -> Optional[Message]:
        if Message.objects.filter(green_api_message_id=green_api_message_id).exists():
            return None

        chat, _ = Chat.objects.get_or_create(client=client)

        message = Message.objects.create(
            chat=chat,
            direction=Message.Direction.INBOUND,
            content=content,
            green_api_message_id=green_api_message_id,
            status=Message.Status.DELIVERED,
        )

        from django.utils import timezone
        chat.last_message_at = timezone.now()
        chat.unread_count += 1
        chat.save(update_fields=['last_message_at', 'unread_count'])

        return message

    @staticmethod
    def save_outbound(client: Client, content: str, ai_model: str = '', tokens: int = 0, latency_ms: int = 0) -> Message:
        chat, _ = Chat.objects.get_or_create(client=client)

        message = Message.objects.create(
            chat=chat,
            direction=Message.Direction.OUTBOUND,
            content=content,
            status=Message.Status.PENDING,
            is_ai_generated=True,
            ai_model_used=ai_model,
            ai_tokens_used=tokens,
            ai_latency_ms=latency_ms,
        )

        from django.utils import timezone
        chat.last_message_at = timezone.now()
        chat.save(update_fields=['last_message_at'])

        return message


class GreenAPIClient:

    def __init__(self):
        self.instance_id = settings.GREEN_API_INSTANCE_ID
        self.token = settings.GREEN_API_TOKEN
        self.base_url = settings.GREEN_API_BASE_URL

    def _url(self, method: str) -> str:
        return f'{self.base_url}/waInstance{self.instance_id}/{method}/{self.token}'

    def send_message(self, chat_id: str, message: str) -> dict:
        url = self._url('sendMessage')
        payload = {
            'chatId': chat_id,
            'message': message,
        }

        start = time.time()
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(url, json=payload)
                response.raise_for_status()
                latency_ms = int((time.time() - start) * 1000)
                data = response.json()
                logger.info(f'Message sent to {chat_id}, id={data.get("idMessage")}, latency={latency_ms}ms')
                return {'success': True, 'id_message': data.get('idMessage'), 'latency_ms': latency_ms}

        except httpx.HTTPStatusError as e:
            logger.error(f'Green API HTTP error: {e.response.status_code} - {e.response.text}')
            return {'success': False, 'error': str(e)}
        except httpx.RequestError as e:
            logger.error(f'Green API request error: {e}')
            return {'success': False, 'error': str(e)}

    def get_instance_state(self) -> dict:
        url = self._url('getStateInstance')
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(url)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            return {'stateInstance': 'error', 'error': str(e)}


green_api = GreenAPIClient()
