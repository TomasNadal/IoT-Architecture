import pytest
from unittest.mock import Mock, patch
from src.services.empresa_service import EmpresaService
from src.domain.model import Empresa

def test_get_empresas_without_permission():
    # Arrange
    mock_repo = Mock()
    mock_queries = Mock()
    service = EmpresaService(mock_repo, mock_queries)
    
    # Act & Assert
    with pytest.raises(ValueError, match="Insufficient permissions"):
        service.get_empresas(user_permissions=[])

def test_get_empresas_with_permission():
    # Arrange
    mock_repo = Mock()
    mock_queries = Mock()
    mock_empresa = Empresa(name="Test", phone_number="123", email="test@test.com")
    mock_repo.get_all.return_value = [mock_empresa]
    
    service = EmpresaService(mock_repo, mock_queries)
    
    # Act
    result = service.get_empresas(user_permissions=['view_empresas'])
    
    # Assert
    assert len(result) == 1
    assert result[0]['name'] == "Test"
    mock_repo.get_all.assert_called_once()

def test_create_empresa_without_permission():
    # Arrange
    mock_repo = Mock()
    mock_queries = Mock()
    service = EmpresaService(mock_repo, mock_queries)
    
    # Act & Assert
    with pytest.raises(ValueError, match="Insufficient permissions"):
        service.create_empresa({}, user_permissions=[])

def test_create_empresa_with_missing_fields():
    # Arrange
    mock_repo = Mock()
    mock_queries = Mock()
    service = EmpresaService(mock_repo, mock_queries)
    
    # Act & Assert
    with pytest.raises(ValueError, match="Missing required fields"):
        service.create_empresa({}, user_permissions=['manage_empresa'])

def test_create_empresa_success():
    # Arrange
    mock_repo = Mock()
    mock_queries = Mock()
    service = EmpresaService(mock_repo, mock_queries)
    
    data = {
        'name': 'Test Empresa',
        'phone_number': '1234567890',
        'email': 'test@test.com'
    }
    
    # Act
    result = service.create_empresa(data, user_permissions=['manage_empresa'])
    
    # Assert
    assert result['name'] == data['name']
    assert result['phone_number'] == data['phone_number']
    mock_repo.add.assert_called_once() 