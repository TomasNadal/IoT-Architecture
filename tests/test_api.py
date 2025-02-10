import pytest
from datetime import datetime
from src.domain import model as m

def test_create_signal(test_client, session):
    # Create test empresa and controlador first
    empresa = m.Empresa(
        name="Test Empresa", 
        phone_number="9999999999", 
        email="test@example.com"
    )
    controlador = m.Controlador(
        name="Test Controller", 
        phone_number="1234567890",  # This matches the signal_data controlador_id
        config={}
    )
    controlador._empresa = empresa
    
    session.add(empresa)
    session.add(controlador)
    session.commit()

    # Sample test data
    signal_data = {
        "controlador_id": "1234567890",
        "sensor_values": [1, 0, 1],
        "location": "test location"
    }
    
    response = test_client.post(
        "/api/signals",
        json=signal_data,
        content_type='application/json'
    )
    
    assert response.status_code == 201
    assert "signal_id" in response.json
    assert "timestamp" in response.json

def test_get_signals(test_client, session):
    response = test_client.get(
        "/api/signals/1",
        query_string={
            "start_time": datetime.now().isoformat(),
            "end_time": datetime.now().isoformat(),
            "user_id": 1
        }
    )
    
    assert response.status_code == 200 