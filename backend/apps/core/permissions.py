"""Custom permissions for multi-tenant access control."""
from rest_framework.permissions import BasePermission


class TenantPermission(BasePermission):
    """
    Permission class that enforces tenant-level access control.
    Objects must have a `tenant` attribute or belong to a tenant.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_superuser:
            return True
        # Check for tenant attribute on the object or through related objects
        if hasattr(obj, "tenant"):
            return obj.tenant == user.tenant
        if hasattr(obj, "production_line") and hasattr(obj.production_line, "tenant"):
            return obj.production_line.tenant == user.tenant
        if hasattr(obj, "machine") and hasattr(obj.machine, "production_line"):
            return obj.machine.production_line.tenant == user.tenant
        if hasattr(obj, "user"):
            return obj.user.tenant == user.tenant
        return False


class IsOwner(BasePermission):
    """Permission for tenant owners only."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == "owner"
        )


class IsAdmin(BasePermission):
    """Permission for admins and owners."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in ("owner", "admin")
        )


class IsManager(BasePermission):
    """Permission for managers, admins, and owners."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in ("owner", "admin", "manager")
        )