from django.urls import path
from .views import UserProfileView, UserListView, UserDetailView, UserPasswordView

urlpatterns = [
    path('', UserListView.as_view(), name='user-list'),
    path('me/', UserProfileView.as_view(), name='user-profile'),
    path('<int:pk>/password/', UserPasswordView.as_view(), name='user-password'),
    path('<int:pk>/', UserDetailView.as_view(), name='user-detail'),
]
