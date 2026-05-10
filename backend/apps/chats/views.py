import django_filters
from rest_framework import generics, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Chat
from .serializers import ChatSerializer
from apps.messaging.models import Message
from apps.messaging.serializers import MessageSerializer


class ChatFilter(django_filters.FilterSet):
    status = django_filters.CharFilter(field_name='status')
    date_from = django_filters.DateTimeFilter(field_name='last_message_at', lookup_expr='gte')
    date_to = django_filters.DateTimeFilter(field_name='last_message_at', lookup_expr='lte')

    class Meta:
        model = Chat
        fields = ['status', 'date_from', 'date_to']


class ChatListView(generics.ListAPIView):
    queryset = Chat.objects.select_related('client').order_by('-last_message_at')
    serializer_class = ChatSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['client__phone', 'client__name']
    filterset_class = ChatFilter


class ChatDetailView(generics.RetrieveUpdateAPIView):
    queryset = Chat.objects.select_related('client')
    serializer_class = ChatSerializer


class ChatMessagesView(generics.ListAPIView):
    serializer_class = MessageSerializer

    def get_queryset(self):
        return Message.objects.filter(
            chat_id=self.kwargs['pk']
        ).order_by('created_at')
