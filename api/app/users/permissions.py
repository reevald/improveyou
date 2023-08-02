from rest_framework import permissions


class EmailValidatedPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        email_validated = request.user.email_validated
        if not email_validated:
            return False
        return True
