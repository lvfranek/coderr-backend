# Third-party
from rest_framework import permissions

# Local imports
from profile_app.models import UserProfile


class IsBusinessUser(permissions.BasePermission):
    """Only business-type users may create offers."""

    def has_permission(self, request, view):
        if request.method != 'POST':
            return True
        profile = getattr(request.user, 'profile', None)
        return bool(profile and profile.type == UserProfile.UserType.BUSINESS)


class IsOfferOwner(permissions.BasePermission):
    """Only the creator of an offer may edit or delete it."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user
