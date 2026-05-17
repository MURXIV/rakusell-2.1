# Развёртывание без Docker

## Требования

- Python 3.11+
- Node.js 20+
- PostgreSQL 15+
- Redis 7+
- ChromaDB

---

## 1. PostgreSQL

Установить PostgreSQL, затем создать БД:

```sql
CREATE USER rakusell WITH PASSWORD '1515';
CREATE DATABASE rakusell OWNER rakusell;
```

---

## 2. Redis

Установить и запустить Redis (порт 6379 по умолчанию).

---

## 3. ChromaDB

```bash
pip install chromadb
chroma run --host 0.0.0.0 --port 8001
```

Или как фоновый процесс:

```bash
nohup chroma run --host 0.0.0.0 --port 8001 &
```

---

## 4. Backend (Django + Daphne + Celery)

```bash
cd backend

# Создать виртуальное окружение
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# Установить зависимости
pip install -r requirements.txt

# Создать .env (скопировать из .env.example и заполнить)
cp .env.example .env
```

Отредактировать `.env` — заменить хосты с `db`/`redis`/`chroma` на `localhost`:

```
DATABASE_URL=postgres://rakusell:rakusell_pass@localhost:5432/rakusell
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2
CHROMA_HOST=localhost
CHROMA_PORT=8001
```

Применить миграции и запустить:

```bash
python manage.py makemigrations users clients chats messaging prompts knowledge logs
python manage.py migrate
python manage.py collectstatic --noinput

# ASGI-сервер
daphne -b 0.0.0.0 -p 8000 core.asgi:application
```

В отдельных терминалах (или через systemd/supervisor):

```bash
# Celery worker
celery -A core worker -l info -Q default,messages,ai

# Celery beat
celery -A core beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

---

## 5. Frontend (Vue + Vite)

```bash
cd frontend
npm install

# Для разработки
npm run dev -- --host 0.0.0.0 --port 3000

# Для продакшена — собрать статику и раздавать через nginx
npm run build
# dist/ → настроить nginx на раздачу
```

---

## 6. Systemd (опционально, для автозапуска на Linux)

Создать файлы сервисов в `/etc/systemd/system/`:

**rakusell-backend.service**
```ini
[Unit]
After=network.target postgresql.service redis.service

[Service]
WorkingDirectory=/path/to/rakusell/backend
ExecStart=/path/to/venv/bin/daphne -b 0.0.0.0 -p 8000 core.asgi:application
EnvironmentFile=/path/to/rakusell/backend/.env
Restart=always

[Install]
WantedBy=multi-user.target
```

**rakusell-worker.service**
```ini
[Unit]
After=network.target redis.service

[Service]
WorkingDirectory=/path/to/rakusell/backend
ExecStart=/path/to/venv/bin/celery -A core worker -l info -Q default,messages,ai
EnvironmentFile=/path/to/rakusell/backend/.env
Restart=always

[Install]
WantedBy=multi-user.target
```

**rakusell-beat.service**
```ini
[Unit]
After=network.target redis.service

[Service]
WorkingDirectory=/path/to/rakusell/backend
ExecStart=/path/to/venv/bin/celery -A core beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
EnvironmentFile=/path/to/rakusell/backend/.env
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
systemctl enable rakusell-backend rakusell-worker rakusell-beat
systemctl start rakusell-backend rakusell-worker rakusell-beat
```
