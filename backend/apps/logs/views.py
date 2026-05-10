from rest_framework import generics, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Log
from .serializers import LogSerializer


class LogListView(generics.ListAPIView):
    queryset = Log.objects.all().order_by('-created_at')
    serializer_class = LogSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_fields = ['log_type', 'level']
    search_fields = ['message']
