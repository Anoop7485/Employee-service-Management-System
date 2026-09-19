from rest_framework.permissions import BasePermission

class IsEmployee(BasePermission):
    def has_permission(self, request, view):
        return request.user.group.filter(
            name='Employee'
        ).exists()

class IsStaffMember(BasePermission):
    def has_permission(self, request, view):
        return request.user.group.filter(name='IT Staff').exists()

class IsManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.group.filter(name='Manager').exists()