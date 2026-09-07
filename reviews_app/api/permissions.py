# Third-party
from rest_framework import permissions

# Local imports
from profile_app.models import UserProfile


class IsCustomerUser(permissions.BasePermission):
    """Only customer-type users may create reviews."""

    def has_permission(self, request, view):
        # Only guard creation; listing stays open to any authenticated user.
        if request.method != 'POST':
            return True
        profile = getattr(request.user, 'profile', None)
        return bool(profile and profile.type == UserProfile.UserType.CUSTOMER)


class IsReviewOwner(permissions.BasePermission):
    """Only the reviewer who created a review may edit or delete it."""

    def has_object_permission(self, request, view, obj):
        # Anyone may read; only the review's author may edit or delete it.
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.reviewer == request.user
