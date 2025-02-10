from dataclasses import dataclass
from typing import List, Set, Optional
from src.domain import model as m	
from sqlalchemy.orm import Session

class UserPermissions:
    def __init__(self, user_id: int, role: str, permissions: Set[str], email: Optional[str] = None):
        self.user_id = user_id
        self.role = role
        self.email = email
        self.permissions = permissions

    def has_permission(self, permission: str) -> bool:
        return permission in self.permissions

    def can_access_empresa(self, empresa_id: int) -> bool:
        # Admin can access all empresas
        if self.role == 'ADMIN':
            return True
        # TODO: Implement empresa-specific access logic
        return False

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
            
        # Cache permissions in Redis (optional)
        cache_key = f"user_permissions:{user_id}"
        self.cache.set(cache_key, list(permissions), ex=3600)  # expire in 1 hour
            
        return UserPermissions(
            user_id=user_id,
            role={r.name for r in roles},
            permissions=permissions
        ) 