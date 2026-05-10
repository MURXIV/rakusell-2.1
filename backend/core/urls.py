from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from core.throttles import LoginRateThrottle


class ThrottledTokenView(TokenObtainPairView):
    throttle_classes = [LoginRateThrottle]


api_v1 = [
    path('auth/token/', ThrottledTokenView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('users/', include('apps.users.urls')),
    path('clients/', include('apps.clients.urls')),
    path('chats/', include('apps.chats.urls')),
    path('messages/', include('apps.messaging.urls')),
    path('ai/', include('apps.ai.urls')),
    path('prompts/', include('apps.prompts.urls')),
    path('knowledge/', include('apps.knowledge.urls')),
    path('logs/', include('apps.logs.urls')),
    path('monitoring/', include('apps.monitoring.urls')),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include(api_v1)),
    path('webhook/', include('apps.webhooks.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
