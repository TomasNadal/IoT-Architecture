from dataclasses import dataclass
from typing import List, Set

@dataclass
class UserPermissions:
    user_id: int
    roles: Set[str]
    permissions: Set[str]

class PermissionQueries:
    def __init__(self, session: Session):
        self.session = session
    
    def get_user_permissions(self, user_id: int) -> UserPermissions:
        # Query user roles and permissions
        roles = self.session.query(m.Role)\
            .join(m.UserRole)\
            .filter(m.UserRole.user_id == user_id)\
            .all()
            
        permissions = set()
        for role in roles:
            permissions.update(role.permissions)
            
        return UserPermissions(
            user_id=user_id,
            roles={r.name for r in roles},
            permissions=permissions
        ) 