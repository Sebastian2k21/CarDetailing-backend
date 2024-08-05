from rest_framework import status

from core.exceptions import ServiceException
from core.models import AppUser, Role


class UserManager:
    def get_role(self, user: 'AppUser'):
        role = Role.objects.filter(id=user.role_id).first()
        if not role:
            raise ServiceException(message="Invalid user role", status_code=status.HTTP_400_BAD_REQUEST)
        return {
            "role_id": role.id,
            "role_name": role.name,
            "role_display_name": role.display_name
        }
