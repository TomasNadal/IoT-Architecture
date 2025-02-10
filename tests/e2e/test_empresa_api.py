import pytest
from datetime import datetime
from unittest.mock import patch
from src.domain.model import Empresa
from src.adapters.repository import EmpresaRepository
from src.queries.queries import SignalQueries

def test_create_empresa_e2e(test_client, session):
    # Arrange
    data = {
        'name': 'E2E Test Empresa',
        'phone_number': '1234567890',
        'email': 'e2e@test.com'
    }
    
    # Mock authenticated user with permissions
    with patch('src.entrypoints.auth.g') as mock_g:
        mock_g.current_user.permissions = ['manage_empresa']
        
        # Act
        response = test_client.post(
            '/api/empresas/',
            json=data,
            content_type='application/json'
        )
    
    # Assert
    assert response.status_code == 201
    assert 'id' in response.json
    
    # Verify in database
    saved_empresa = session.query(Empresa).filter_by(email='e2e@test.com').first()
    assert saved_empresa is not None
    assert saved_empresa.name == data['name']

def test_get_empresas_e2e(test_client, session):
    # Reference existing test helper
    # See test_repository.py lines 28-41 for insert_empresa function
    empresa_id = insert_empresa(session)
    
    # Mock authenticated user with permissions
    with patch('src.entrypoints.auth.g') as mock_g:
        mock_g.current_user.permissions = ['view_empresas']
        
        # Act
        response = test_client.get('/api/empresas/')
    
    # Assert
    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]['name'] == 'Test Empresa'

def test_unauthorized_access_e2e(test_client):
    # Mock authenticated user without permissions
    with patch('src.entrypoints.auth.g') as mock_g:
        mock_g.current_user.permissions = []
        
        # Act
        response = test_client.get('/api/empresas/')
    
    # Assert
    assert response.status_code == 403 