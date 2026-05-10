from django.urls import path
from .views import KnowledgeListView, KnowledgeDetailView

urlpatterns = [
    path('', KnowledgeListView.as_view(), name='knowledge-list'),
    path('<int:pk>/', KnowledgeDetailView.as_view(), name='knowledge-detail'),
]
