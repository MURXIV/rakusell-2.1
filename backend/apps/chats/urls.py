from django.urls import path
from .views import ChatListView, ChatDetailView, ChatMessagesView

urlpatterns = [
    path('', ChatListView.as_view(), name='chat-list'),
    path('<int:pk>/', ChatDetailView.as_view(), name='chat-detail'),
    path('<int:pk>/messages/', ChatMessagesView.as_view(), name='chat-messages'),
]
