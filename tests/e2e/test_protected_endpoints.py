import pytest
from datetime import datetime
from unittest.mock import patch

def test_unauthorized_empresa_access(test_client, session):
    # Reference existing test helper
    empresa_id = insert_empresa(session)
    
    # Mock user without permissions
    with patch('src.entrypoints.auth.g') as mock_g:
        mock_g.current_user.permissions = []
        
        # Test various endpoints
        endpoints = [
            f'/api/empresas/{empresa_id}',
            f'/api/empresas/{empresa_id}/dashboard',
            f'/api/empresas/{empresa_id}/components'
        ]
        
        for endpoint in endpoints:
            response = test_client.get(endpoint)
            assert response.status_code == 403

def test_authorized_empresa_access(test_client, session):
    # Reference existing test helper for setup
    empresa_id = insert_empresa(session)
    
    # Mock user with permissions
    with patch('src.entrypoints.auth.g') as mock_g:
        mock_g.current_user.permissions = ['view_empresas', 'view_dashboard']
        
        # Test dashboard access
        response = test_client.get(f'/api/empresas/{empresa_id}/dashboard')
        assert response.status_code == 200
        
        # Test empresa details access
        response = test_client.get(f'/api/empresas/{empresa_id}')
        assert response.status_code == 200

def test_admin_full_access(test_client, session):
    # Setup test data referencing existing helpers
    empresa_id = insert_empresa(session)
    controlador_id = insert_controlador(session, empresa_id)
    
    # Mock admin user
    with patch('src.entrypoints.auth.g') as mock_g:
        mock_g.current_user.permissions = [p.value for p in Permission]
        
        # Test full access to all endpoints
        endpoints = [
            ('GET', f'/api/empresas/{empresa_id}'),
            ('PUT', f'/api/empresas/{empresa_id}'),
            ('DELETE', f'/api/empresas/{empresa_id}'),
            ('GET', f'/api/controlador/{controlador_id}/detail'),
            ('GET', f'/api/dashboard/empresa/{empresa_id}/dashboard')
        ]
        
        for method, endpoint in endpoints:
            response = test_client.open(endpoint, method=method)
            assert response.status_code in [200, 201] 