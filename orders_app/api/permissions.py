# Third-party
from rest_framework import permissions

# Local imports
from profile_app.models import UserProfile


class IsCustomerUser(permissions.BasePermission):
    """Only customer-type users may create orders."""

    def has_permission(self, request, view):
        if request.method != 'POST':
            return True
        profile = getattr(request.user, 'profile', None)
        return bool(profile and profile.type == UserProfile.UserType.CUSTOMER)


class IsBusinessUserForOrder(permissions.BasePermission):
    """Only the business user of an order may update its status."""

    def has_object_permission(self, request, view, obj):
        if request.method != 'PATCH':
            return True
        return obj.business_user == request.user


class IsStaffUser(permissions.BasePermission):
    """Only staff/admin users may delete orders."""

    def has_object_permission(self, request, view, obj):
        return request.user.is_staff
