import logging
import time
from typing import Optional

from django.conf import settings

logger = logging.getLogger(__name__)


class AIService:

    def __init__(self):
        self.provider = settings.AI_PROVIDER
        self.model = settings.AI_MODEL
        self.max_tokens = settings.AI_MAX_TOKENS
        self.history_limit = settings.AI_HISTORY_LIMIT

    def generate_response(
        self,
        system_prompt: str,
        history: list[dict],
        user_message: str,
        context: str = '',
        client_context: str = '',
    ) -> dict:
        full_system = system_prompt
        if client_context:
            full_system += f'\n\n--- Информация о клиенте ---\n{client_context}\n--- Конец информации о клиенте ---'
        if context:
            full_system += f'\n\n--- Relevant context ---\n{context}\n--- End context ---'

        trimmed_history = history[-self.history_limit:]

        start = time.time()

        if self.provider == 'openai':
            result = self._openai(full_system, trimmed_history, user_message)
        elif self.provider == 'deepseek':
            result = self._deepseek(full_system, trimmed_history, user_message)
        elif self.provider == 'gemini':
            result = self._gemini(full_system, trimmed_history, user_message)
        else:
            raise ValueError(f'Unknown AI provider: {self.provider}')

        result['latency_ms'] = int((time.time() - start) * 1000)
        result['model'] = self.model
        return result

    def _openai(self, system_prompt: str, history: list, user_message: str) -> dict:
        from openai import OpenAI

        client = OpenAI(api_key=settings.OPENAI_API_KEY)

        messages = [{'role': 'system', 'content': system_prompt}]
        messages.extend(history)
        messages.append({'role': 'user', 'content': user_message})

        response = client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=self.max_tokens,
            temperature=0.7,
        )

        return {
            'content': response.choices[0].message.content,
            'tokens': response.usage.total_tokens,
        }

    def _deepseek(self, system_prompt: str, history: list, user_message: str) -> dict:
        from openai import OpenAI

        client = OpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url='https://api.deepseek.com/v1',
        )

        messages = [{'role': 'system', 'content': system_prompt}]
        messages.extend(history)
        messages.append({'role': 'user', 'content': user_message})

        response = client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=self.max_tokens,
            temperature=0.7,
        )

        return {
            'content': response.choices[0].message.content,
            'tokens': response.usage.total_tokens,
        }

    def _gemini(self, system_prompt: str, history: list, user_message: str) -> dict:
        import google.generativeai as genai

        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel(
            model_name=self.model,
            system_instruction=system_prompt,
        )

        gemini_history = []
        for msg in history:
            role = 'user' if msg['role'] == 'user' else 'model'
            gemini_history.append({'role': role, 'parts': [msg['content']]})

        chat = model.start_chat(history=gemini_history)
        response = chat.send_message(user_message)

        return {
            'content': response.text,
            'tokens': response.usage_metadata.total_token_count if hasattr(response, 'usage_metadata') else 0,
        }


ai_service = AIService()
