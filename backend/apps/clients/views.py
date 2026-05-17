from rest_framework import generics, filters
from rest_framework.permissions import IsAuthenticated
from apps.users.permissions import IsAdminOrReadOnly
from .models import Client
from .serializers import ClientSerializer, ClientDetailSerializer


class ClientListView(generics.ListAPIView):
    queryset = Client.objects.all().order_by('-last_seen')
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['phone', 'name', 'tags']


class ClientDetailView(generics.RetrieveUpdateAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientDetailSerializer
    permission_classes = [IsAdminOrReadOnly]
