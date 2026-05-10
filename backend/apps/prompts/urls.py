from django.urls import path
from .views import PromptListView, PromptDetailView, ActivePromptView

urlpatterns = [
    path('', PromptListView.as_view(), name='prompt-list'),
    path('<int:pk>/', PromptDetailView.as_view(), name='prompt-detail'),
    path('active/', ActivePromptView.as_view(), name='prompt-active'),
]
