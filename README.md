# Rakusell WhatsApp AI чат-бот

Система для автоматических ответов клиентам в WhatsApp через ИИ, есть админка для управления чатами, клиентами и промптами

## Что умеет

- Принимает сообщения из WhatsApp через Green API вебхук
- Генерирует ответы через AI (DeepSeek (~2$ в использовании(+)) / OpenAI(-) / Gemini(-))
- Помнит историю диалога каждого клиента
- Ищет информацию в базе знаний перед ответом (RAG)
- Показывает всё в админке в реальном времени

## Стек

- Django + PostgreSQL + Redis
- Celery для очередей
- ChromaDB для векторного поиска
- Vue 3 + Tailwind для фронта
- Green API для WhatsApp
- Docker Compose всё это запускает

## Запуск

```bash
cp backend/.env.example backend/.env
# заполнить ключи в .env (таблица с ключами прилагается отдельно)

docker-compose up --build
```

Создать админа:

```bash
docker-compose exec backend python manage.py createsuperuser
```

Открыть: http://localhost:3000

## Переменные окружения

Скопировать `backend/.env.example` → `backend/.env` и заполнить:

```
GREEN_API_INSTANCE_ID=1
GREEN_API_TOKEN=2
DEEPSEEK_API_KEY=3
OPENAI_API_KEY=4
GEMINI_API_KEY=5
```

Расшифровка цифр — в таблице которую я скину отдельно.

## Вебхук

Green API должен слать вебхуки на:

```
https://твой-домен/webhook/whatsapp/
```

Для локальной разработки нужен ngrok.
