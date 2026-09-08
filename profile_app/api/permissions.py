from rest_framework import permissions


class IsProfileOwner(permissions.BasePermission):
    """Only the profile owner may edit their own profile (PATCH)."""

    def has_object_permission(self, request, view, obj):
        """Anyone may read a profile; only the owner may edit it."""
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user
