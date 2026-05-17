"""
Field-level encryption using Fernet (AES-128-CBC + HMAC-SHA256).
Set FIELD_ENCRYPTION_KEY in .env (generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
"""
from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings

_fernet = None

# Fernet tokens always start with this prefix when base64-decoded
_FERNET_PREFIX = b'gAAAAA'


def _get_fernet() -> Fernet:
    global _fernet
    if _fernet is None:
        key = getattr(settings, 'FIELD_ENCRYPTION_KEY', '')
        if not key:
            raise ValueError('FIELD_ENCRYPTION_KEY is not set in settings/.env')
        _fernet = Fernet(key.encode() if isinstance(key, str) else key)
    return _fernet


def _is_encrypted(value: str) -> bool:
    """Check if value is already a Fernet token (starts with gAAAAA)."""
    return bool(value) and value.startswith('gAAAAA')


def encrypt(value: str) -> str:
    if not value or _is_encrypted(value):
        return value
    return _get_fernet().encrypt(value.encode('utf-8')).decode('ascii')


def decrypt(value: str) -> str:
    if not value:
        return value
    try:
        return _get_fernet().decrypt(value.encode('ascii')).decode('utf-8')
    except InvalidToken:
        if _is_encrypted(value):
            return '[Не удалось расшифровать: проверьте FIELD_ENCRYPTION_KEY]'
        return value
    except Exception:
        if _is_encrypted(value):
            return '[Не удалось расшифровать: проверьте FIELD_ENCRYPTION_KEY]'
        return value
