from bson import ObjectId
from rest_framework import permissions

from .models import Role


class HasRole(permissions.BasePermission):
    def __init__(self, role_name):
        self.role_name = role_name

    def has_permission(self, request, view):
        role = Role.objects.filter(_id=ObjectId(request.user.role_id)).first()
        if not role or role.name != self.role_name:
             return False
        return True


class IsDetailer(HasRole):
    message = 'This action is only for detailer.'

    def __init__(self):
        super().__init__("detailer")


class IsClient(HasRole):
    message = 'This action is only for client.'

    def __init__(self):
        super().__init__("client")