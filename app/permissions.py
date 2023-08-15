from rest_framework.permissions import BasePermission


class GetShop(BasePermission):
    def has_permission(self, request, view):

        if request.method == "GET":
            return True
        return False


class IsStaff(BasePermission):
    def has_permission(self, request, view):

        if request.method == "GET":
            return True
        return request.user.is_superuser
