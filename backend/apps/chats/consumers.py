import json
import logging

from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.group_name = f'chat_{self.chat_id}'

        user = self.scope.get('user')
        if not user or not user.is_authenticated:
            await self.close(code=4001)
            return

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        logger.info(f'WS connected: {self.group_name}')

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            action = data.get('action')

            if action == 'ping':
                await self.send(text_data=json.dumps({'action': 'pong'}))

        except json.JSONDecodeError:
            pass

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'message',
            'data': event['message'],
        }))

    async def chat_status(self, event):
        await self.send(text_data=json.dumps({
            'type': 'status',
            'data': event['status'],
        }))
