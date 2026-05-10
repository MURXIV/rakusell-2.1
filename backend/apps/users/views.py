from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import User
from .serializers import UserSerializer
from .permissions import IsAdmin


class UserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class UserListView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]


class ResetPasswordView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username', '').strip()
        new_password = request.data.get('new_password', '').strip()

        if not username or not new_password or len(new_password) < 6:
            return Response({'error': 'Invalid data'}, status=400)

        try:
            user = User.objects.get(username=username)
            user.set_password(new_password)
            user.save()
            return Response({'status': 'ok'})
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=404)
