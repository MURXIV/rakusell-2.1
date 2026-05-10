import logging
from typing import Optional

logger = logging.getLogger(__name__)


class LogService:
    """Convenience wrapper for creating Log entries."""

    @staticmethod
    def _create(level: str, log_type: str, message: str, client=None, payload: dict = None, traceback: str = ''):
        try:
            from .models import Log
            Log.objects.create(
                log_type=log_type,
                level=level,
                client=client,
                message=message,
                payload=payload or {},
                error_traceback=traceback,
            )
        except Exception as e:
            logger.error(f'Failed to write log: {e}')

    @classmethod
    def info(cls, log_type: str, message: str, client=None, payload: dict = None):
        cls._create('info', log_type, message, client, payload)

    @classmethod
    def warning(cls, log_type: str, message: str, client=None, payload: dict = None):
        cls._create('warning', log_type, message, client, payload)

    @classmethod
    def error(cls, log_type: str, message: str, client=None, payload: dict = None, traceback: str = ''):
        cls._create('error', log_type, message, client, payload, traceback)
