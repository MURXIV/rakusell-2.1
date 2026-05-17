from datetime import timedelta
from time import perf_counter

from django.db import connection
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def health_check(request):
    checks = {}
    overall = 'ok'

    # PostgreSQL
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
        checks['database'] = {'status': 'ok'}
    except Exception as e:
        checks['database'] = {'status': 'error', 'detail': str(e)}
        overall = 'degraded'

    # Redis
    try:
        from django.conf import settings
        import redis
        r = redis.from_url(settings.CELERY_BROKER_URL, socket_connect_timeout=1, socket_timeout=1)
        r.ping()
        checks['redis'] = {'status': 'ok'}
    except Exception as e:
        checks['redis'] = {'status': 'error', 'detail': str(e)}
        overall = 'degraded'

    # ChromaDB
    try:
        from django.conf import settings
        import chromadb
        client = chromadb.HttpClient(host=settings.CHROMA_HOST, port=settings.CHROMA_PORT)
        start = perf_counter()
        client.heartbeat()
        checks['chromadb'] = {'status': 'ok', 'latency_ms': int((perf_counter() - start) * 1000)}
    except Exception as e:
        checks['chromadb'] = {'status': 'error', 'detail': str(e)}
        overall = 'degraded'

    # Celery workers
    try:
        from core.celery import app as celery_app
        ping = celery_app.control.inspect(timeout=1).ping() or {}
        worker_count = len(ping)
        if worker_count == 0:
            raise RuntimeError('No active Celery workers responded')
        checks['celery'] = {
            'status': 'ok',
            'workers': worker_count,
            'worker_names': list(ping.keys()),
        }
    except Exception as e:
        checks['celery'] = {'status': 'error', 'detail': str(e)}
        overall = 'degraded'

    return Response({
        'status': overall,
        'timestamp': timezone.now().isoformat(),
        'checks': checks,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def queue_stats(request):
    try:
        from django.conf import settings
        import redis
        r = redis.from_url(settings.CELERY_BROKER_URL)

        queues = ['default', 'messages', 'ai']
        result = {}
        for q in queues:
            result[q] = r.llen(q)

        return Response({'queues': result})
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def system_stats(request):
    from apps.chats.models import Chat
    from apps.clients.models import Client
    from apps.messaging.models import Message

    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    last_24h = now - timedelta(hours=24)

    # Avg AI latency over last 100 AI messages
    ai_latencies = list(
        Message.objects.filter(is_ai_generated=True, ai_latency_ms__gt=0)
        .order_by('-created_at')
        .values_list('ai_latency_ms', flat=True)[:100]
    )
    avg_latency_ms = int(sum(ai_latencies) / len(ai_latencies)) if ai_latencies else 0

    return Response({
        'chats': {
            'total': Chat.objects.count(),
            'active': Chat.objects.filter(status='active').count(),
            'pending': Chat.objects.filter(status='pending').count(),
            'closed': Chat.objects.filter(status='closed').count(),
        },
        'messages': {
            'total': Message.objects.count(),
            'today': Message.objects.filter(created_at__gte=today_start).count(),
            'last_24h': Message.objects.filter(created_at__gte=last_24h).count(),
            'failed': Message.objects.filter(status='failed').count(),
            'ai_generated': Message.objects.filter(is_ai_generated=True).count(),
        },
        'clients': {
            'total': Client.objects.count(),
            'active_today': Client.objects.filter(last_seen__gte=today_start).count(),
            'blocked': Client.objects.filter(is_blocked=True).count(),
        },
        'performance': {
            'avg_ai_latency_ms': avg_latency_ms,
            'sla_ok': avg_latency_ms < 3000,
        },
    })
