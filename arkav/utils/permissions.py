from rest_framework.permissions import BasePermission
from rest_framework.permissions import IsAuthenticated


class IsNotAuthenticated(BasePermission):
    def has_permission(self, request, view):
        return not IsAuthenticated().has_permission(request, view)
