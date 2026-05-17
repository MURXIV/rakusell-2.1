import os
from pathlib import Path
from datetime import timedelta
import environ
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(BASE_DIR / '.env')

SECRET_KEY = env('SECRET_KEY', default='')
DEBUG = env.bool('DEBUG', default=False)
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1'] if DEBUG else [])

if not SECRET_KEY:
    raise ImproperlyConfigured('SECRET_KEY must be set in backend/.env')
if not DEBUG and not ALLOWED_HOSTS:
    raise ImproperlyConfigured('ALLOWED_HOSTS must be set when DEBUG=False')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'channels',
    'django_celery_beat',
    'django_celery_results',
    'django_filters',
    'apps.users',
    'apps.clients',
    'apps.chats',
    'apps.messaging',
    'apps.webhooks',
    'apps.ai',
    'apps.rag',
    'apps.prompts',
    'apps.knowledge',
    'apps.logs',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

ASGI_APPLICATION = 'core.asgi.application'

DATABASES = {
    'default': env.db('DATABASE_URL', default='postgres://rakusell:rakusell_pass@localhost:5432/rakusell')
}

REDIS_URL = env('REDIS_URL', default='redis://localhost:6379/0')

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [REDIS_URL],
        },
    },
}

CELERY_BROKER_URL = env('CELERY_BROKER_URL', default='redis://localhost:6379/1')
CELERY_RESULT_BACKEND = env('CELERY_RESULT_BACKEND', default='redis://localhost:6379/2')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_ACKS_LATE = True
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERY_TASK_QUEUES_MAX_PRIORITY = 10
CELERY_TASK_DEFAULT_QUEUE = 'default'

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=env.int('JWT_ACCESS_TOKEN_LIFETIME_MINUTES', default=60)),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=env.int('JWT_REFRESH_TOKEN_LIFETIME_DAYS', default=7)),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '60/hour',
        'user': '2000/hour',
        'login': '10/minute',
        'webhook': '600/minute',
    },
}

CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS', default=[
    'http://localhost:3000',
    'http://127.0.0.1:3000',
])
CORS_ALLOW_CREDENTIALS = True

AUTH_USER_MODEL = 'users.User'

GREEN_API_INSTANCE_ID = env('GREEN_API_INSTANCE_ID', default='')
GREEN_API_TOKEN = env('GREEN_API_TOKEN', default='')
GREEN_API_BASE_URL = env('GREEN_API_BASE_URL', default='https://api.green-api.com')

AI_PROVIDER = env('AI_PROVIDER', default='openai')
OPENAI_API_KEY = env('OPENAI_API_KEY', default='')
GEMINI_API_KEY = env('GEMINI_API_KEY', default='')
DEEPSEEK_API_KEY = env('DEEPSEEK_API_KEY', default='')
AI_MODEL = env('AI_MODEL', default='gpt-4o-mini')
AI_MAX_TOKENS = env.int('AI_MAX_TOKENS', default=1000)
AI_HISTORY_LIMIT = env.int('AI_HISTORY_LIMIT', default=20)
AI_PROMPT_SCENARIO = env('AI_PROMPT_SCENARIO', default='sales')
AI_TIMEOUT_SECONDS = env.int('AI_TIMEOUT_SECONDS', default=25)
MESSAGE_GROUPING_SECONDS = env.int('MESSAGE_GROUPING_SECONDS', default=25)
BOT_TIME_ZONE = env('BOT_TIME_ZONE', default='Asia/Qyzylorda')
RESPOND_TO_GROUPS = env.bool('RESPOND_TO_GROUPS', default=False)

CHROMA_HOST = env('CHROMA_HOST', default='localhost')
CHROMA_PORT = env.int('CHROMA_PORT', default=8001)
CHROMA_COLLECTION = env('CHROMA_COLLECTION', default='rakusell_knowledge')
RAG_DISTANCE_THRESHOLD = env.float('RAG_DISTANCE_THRESHOLD', default=0.7)
RAG_TOP_K = env.int('RAG_TOP_K', default=5)
RAG_EMBEDDING_PROVIDER = env('RAG_EMBEDDING_PROVIDER', default='local')
RAG_EMBEDDING_MODEL = env('RAG_EMBEDDING_MODEL', default='text-embedding-3-small')

WEBHOOK_SECRET = env('WEBHOOK_SECRET', default='')

FIELD_ENCRYPTION_KEY = env('FIELD_ENCRYPTION_KEY', default='')

if not DEBUG and not WEBHOOK_SECRET:
    raise ImproperlyConfigured('WEBHOOK_SECRET must be set when DEBUG=False')
if not FIELD_ENCRYPTION_KEY:
    raise ImproperlyConfigured('FIELD_ENCRYPTION_KEY must be set in backend/.env')

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ── Security headers (safe in both dev and prod) ──────────────────────────────
SECURE_CONTENT_TYPE_NOSNIFF = True       # X-Content-Type-Options: nosniff
X_FRAME_OPTIONS = 'DENY'                 # X-Frame-Options: DENY
SECURE_BROWSER_XSS_FILTER = True         # X-XSS-Protection (older browsers)

# In production set these via nginx/reverse-proxy or enable here:
# SECURE_SSL_REDIRECT = True
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True
# SECURE_HSTS_SECONDS = 31536000

LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = BOT_TIME_ZONE
USE_I18N = True
USE_TZ = True
