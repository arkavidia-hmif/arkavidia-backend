from rest_framework.permissions import BasePermission


class IsNotAuthenticated(BasePermission):
    def has_permission(self, request, view):
        return (not request.user) or (not request.user.is_email_confirmed)
