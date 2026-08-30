# Third-party
from rest_framework import permissions


class IsProfileOwner(permissions.BasePermission):
    """Only the profile owner may edit their own profile (PATCH)."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user
