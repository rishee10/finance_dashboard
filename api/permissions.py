from rest_framework.permissions import BasePermission


class IsAdminRole(BasePermission):
    """Only admin-role users may proceed."""
    message = "Admin role required."

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.is_admin
        )


class IsAnalystOrAbove(BasePermission):
    """Analyst or admin users may proceed."""
    message = "Analyst or Admin role required."

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.is_analyst  # property covers analyst + admin
        )


class IsViewerOrAbove(BasePermission):
    """Any authenticated active user may proceed (viewer is lowest role)."""
    message = "Active account required."

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.is_active
        )