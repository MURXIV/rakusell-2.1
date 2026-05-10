from django.urls import path
from . import views

urlpatterns = [
    path('health/', views.health_check, name='health'),
    path('health/queues/', views.queue_stats, name='queue_stats'),
    path('health/stats/', views.system_stats, name='system_stats'),
]
