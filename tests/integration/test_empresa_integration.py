import pytest
from datetime import datetime
from src.services.empresa_service import EmpresaService
from src.adapters.repository import EmpresaRepository
from src.queries.queries import SignalQueries

def test_empresa_service_integration(session):
    # Arrange
    repo = EmpresaRepository(session)
    queries = SignalQueries(session)
    service = EmpresaService(repo, queries)
    
    # Reference existing test helper
    # See test_repository.py lines 28-41 for insert_empresa function
    empresa_id = insert_empresa(session)
    
    # Act
    result = service.get_empresas(user_permissions=['view_empresas'])
    
    # Assert
    assert len(result) == 1
    assert result[0]['name'] == "Test Empresa"
    assert result[0]['email'] == "test@example.com"

def test_empresa_creation_integration(session):
    # Arrange
    repo = EmpresaRepository(session)
    queries = SignalQueries(session)
    service = EmpresaService(repo, queries)
    
    data = {
        'name': 'New Empresa',
        'phone_number': '9999999999',
        'email': 'new@test.com'
    }
    
    # Act
    result = service.create_empresa(data, user_permissions=['manage_empresa'])
    
    # Assert
    saved_empresa = repo.get(result['id'])
    assert saved_empresa.name == data['name']
    assert saved_empresa.email == data['email'] 