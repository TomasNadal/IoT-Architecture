import pytest
from unittest.mock import Mock, patch
from src.domain.model import Role, Permission
from src.services.auth import UserPermissions, PermissionQueries

def test_admin_has_all_permissions():
    # Arrange
    mock_session = Mock()
    mock_role = Mock(name='admin', permissions=[p.value for p in Permission])
    mock_session.query().join().filter().all.return_value = [mock_role]
    
    queries = PermissionQueries(mock_session)
    
    # Act
    permissions = queries.get_user_permissions(user_id=1)
    
    # Assert
    assert 'view_dashboard' in permissions.permissions
    assert 'manage_empresa' in permissions.permissions
    assert 'manage_users' in permissions.permissions

def test_empresa_user_limited_permissions():
    # Arrange
    mock_session = Mock()
    mock_role = Mock(
        name='empresa_user', 
        permissions=['view_dashboard', 'view_signals']
    )
    mock_session.query().join().filter().all.return_value = [mock_role]
    
    queries = PermissionQueries(mock_session)
    
    # Act
    permissions = queries.get_user_permissions(user_id=1)
    
    # Assert
    assert 'view_dashboard' in permissions.permissions
    assert 'view_signals' in permissions.permissions
    assert 'manage_empresa' not in permissions.permissions 