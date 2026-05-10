from .models import Prompt

DEFAULT_PROMPT = """You are a helpful assistant for Rakusell.

LANGUAGE RULE (most important):
- Detect the language of the user's message automatically
- If user writes in Russian → respond ONLY in Russian
- If user writes in Kazakh → respond ONLY in Kazakh  
- If user writes in English → respond ONLY in English
- If user switches language mid-conversation → switch immediately
- Never mix languages in one response

Be polite, concise and professional."""


class PromptService:

    @staticmethod
    def get_active_prompt(scenario: str = 'general') -> str:
        prompt = Prompt.objects.filter(
            scenario=scenario,
            is_active=True,
        ).first()
        return prompt.system_prompt if prompt else DEFAULT_PROMPT
