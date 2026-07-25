from rest_framework.permissions import SAFE_METHODS, BasePermission

from accounts.models import Account


class IsAdminOrReadOnly(BasePermission):
    message = 'Only administrators can modify user records.'

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False

        if request.method in SAFE_METHODS:
            return True

        return request.user.role == Account.Role.ADMIN
