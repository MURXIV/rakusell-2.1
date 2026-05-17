# Rakusell WhatsApp AI Bot

Admin panel and backend for automatic WhatsApp replies through Green API and an AI provider.

## Stack

- Backend: Django, Django REST Framework, Channels, Celery
- Data: PostgreSQL, Redis, ChromaDB
- Frontend: Vue 3, Vite, Pinia, Tailwind
- Messaging: Green API
- AI: DeepSeek, OpenAI, or Gemini

## Local/Server Setup Without Docker

### 1. Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Edit `backend/.env` before running:

```env
SECRET_KEY=<long-random-secret>
DEBUG=False
ALLOWED_HOSTS=your-domain.com,127.0.0.1
CORS_ALLOWED_ORIGINS=https://your-domain.com
DATABASE_URL=postgres://rakusell:<password>@localhost:5432/rakusell
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2
WEBHOOK_SECRET=<long-random-webhook-secret>
FIELD_ENCRYPTION_KEY=<fernet-key>
```

Generate encryption key:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Run migrations and start the ASGI server:

```bash
python manage.py migrate
python manage.py createsuperuser
daphne -b 0.0.0.0 -p 8000 core.asgi:application
```

Start workers in separate terminals:

```bash
celery -A core worker -l info -Q default,messages,ai
celery -A core beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

### 2. ChromaDB

```bash
pip install chromadb
chroma run --host 0.0.0.0 --port 8001
```

### 3. Frontend

```bash
cd frontend
npm install
npm run build
```

For local development:

```bash
npm run dev -- --host 0.0.0.0 --port 3000
```

Configure frontend environment:

```env
VITE_API_URL=http://localhost:8000/api/v1
VITE_WS_URL=ws://localhost:8000
```

On production use your public HTTPS/WSS URLs.

## Webhook

Green API webhook URL:

```text
https://your-domain.com/webhook/whatsapp/
```

Set `WEBHOOK_SECRET` in production. Without it the application refuses to start when `DEBUG=False`.

## Security Notes

- Do not commit `backend/.env` or `frontend/.env` with real secrets.
- Public password reset is disabled. User password changes must be done by an authenticated admin through user management or Django admin.
- `FIELD_ENCRYPTION_KEY` is required because client phones, context, and messages are encrypted at field level.
