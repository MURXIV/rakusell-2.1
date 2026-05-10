from rest_framework import generics, filters
from .models import Client
from .serializers import ClientSerializer, ClientDetailSerializer


class ClientListView(generics.ListAPIView):
    queryset = Client.objects.all().order_by('-last_seen')
    serializer_class = ClientSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['phone', 'name', 'tags']


class ClientDetailView(generics.RetrieveUpdateAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientDetailSerializer
