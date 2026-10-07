from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """
    Allows access only to Admin users.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == "ADMIN"
        )


class IsFaculty(BasePermission):
    """
    Allows access only to Faculty users.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == "FACULTY"
        )


class IsPlacementCell(BasePermission):
    """
    Allows access only to Placement Cell users.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == "PLACEMENT"
        )


class IsStudent(BasePermission):
    """
    Allows access only to Student users.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == "STUDENT"
        )


class IsAdminOrFaculty(BasePermission):
    """
    Allows access to Admin or Faculty users.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role in ["ADMIN", "FACULTY"]
        )


class IsAdminOrPlacementCell(BasePermission):
    """
    Allows access to Admin or Placement Cell users.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role in ["ADMIN", "PLACEMENT"]
        )


class IsAdminOrFacultyOrPlacementCell(BasePermission):
    """
    Allows access to Admin, Faculty, or Placement Cell users.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role in [
                "ADMIN",
                "FACULTY",
                "PLACEMENT",
            ]
        )