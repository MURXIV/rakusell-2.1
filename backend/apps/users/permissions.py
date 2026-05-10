from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """Only admin role users."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_admin)


class IsAdminOrReadOnly(BasePermission):
    """Admin can write, manager can only read."""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True
        return request.user.is_admin
