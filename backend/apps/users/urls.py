from django.urls import path
from .views import UserProfileView, UserListView, UserDetailView, ResetPasswordView

urlpatterns = [
    path('', UserListView.as_view(), name='user-list'),
    path('me/', UserProfileView.as_view(), name='user-profile'),
    path('<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
]
