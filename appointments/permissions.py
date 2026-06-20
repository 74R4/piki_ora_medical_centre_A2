from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Normal users can view data.
    Staff users can add, edit, and delete data.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user and request.user.is_staff


class IsAdminUserOnly(permissions.BasePermission):
    """
    Only staff users can access this API.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_staff


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Patients can access their own appointment.
    Staff can access all appointments.
    """

    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_staff:
            return True

        return obj.patient == request.user