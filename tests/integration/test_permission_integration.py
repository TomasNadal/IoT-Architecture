import pytest
from src.domain.model import User, Role, Permission
from src.services.auth import PermissionQueries
from src.adapters.repository import UserRepository

def test_user_permission_integration(session):
    # Setup
    user = User("Test", "User", "test@test.com", "password", Role.EMPRESA_USER)
    user_repo = UserRepository(session)
    user_repo.add(user)
    session.commit()
    
    # Exercise
    queries = PermissionQueries(session)
    permissions = queries.get_user_permissions(user.id)
    
    # Assert
    assert 'view_dashboard' in permissions.permissions
    assert 'view_signals' in permissions.permissions
    assert 'manage_empresa' not in permissions.permissions

def test_admin_permission_integration(session):
    # Setup
    admin = User("Admin", "User", "admin@test.com", "password", Role.ADMIN)
    user_repo = UserRepository(session)
    user_repo.add(admin)
    session.commit()
    
    # Exercise
    queries = PermissionQueries(session)
    permissions = queries.get_user_permissions(admin.id)
    
    # Assert
    assert all(p.value in permissions.permissions for p in Permission) 