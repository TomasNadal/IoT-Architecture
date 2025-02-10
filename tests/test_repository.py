import pytest
from datetime import datetime
import json
from sqlalchemy import text
from src.adapters.repository import EmpresaRepository
from src.queries.queries import SignalQueries
import src.domain.model as m

def test_repository_can_save_empresa(session):
    # Prepare
    new_empresa = m.Empresa(
        name="Test Empresa",
        phone_number="1234567890",
        email="test@example.com"
    )
    repo = EmpresaRepository(session)

    # Function to assess
    repo.add(new_empresa)
    session.commit()

    # Verify
    rows = list(session.execute(
        text("SELECT name, phone_number, email FROM empresas")
    ))
    assert rows == [("Test Empresa", "1234567890", "test@example.com")]

def insert_empresa(session):
    session.execute(
        text("INSERT INTO empresas (name, phone_number, email) VALUES (:name, :phone, :email)"),
        {
            "name": "Test Empresa",
            "phone": "1234567890",
            "email": "test@example.com"
        }
    )
    [[empresa_id]] = session.execute(
        text("SELECT id FROM empresas WHERE email = :email"),
        {"email": "test@example.com"}
    )
    return empresa_id

def insert_controlador(session, empresa_id):
    config = json.dumps({"setting1": "value1"})
    session.execute(
        text("""
            INSERT INTO controladores (empresa_id, name, phone_number, config) 
            VALUES (:empresa_id, :name, :phone, :config)
        """),
        {
            "empresa_id": empresa_id,
            "name": "Test Controller",
            "phone": "5555555555",
            "config": config
        }
    )
    [[controlador_id]] = session.execute(
        text("SELECT id FROM controladores WHERE empresa_id = :empresa_id"),
        {"empresa_id": empresa_id}
    )
    return controlador_id

def insert_signal(session, controlador_id):
    values = json.dumps({"temp": 25.5})
    metadata = json.dumps({"source": "sensor1"})
    tstamp = datetime(2024, 1, 1, 12, 0)
    
    session.execute(
        text("""
            INSERT INTO signals 
            (controlador_id, tstamp, values, latitude, longitude, metadata)
            VALUES 
            (:controlador_id, :tstamp, :values, :lat, :lon, :metadata)
        """),
        {
            "controlador_id": controlador_id,
            "tstamp": tstamp,
            "values": values,
            "lat": 40.7128,
            "lon": -74.006,
            "metadata": metadata
        }
    )
    [[signal_id]] = session.execute(
        text("SELECT id FROM signals WHERE controlador_id = :controlador_id"),
        {"controlador_id": controlador_id}
    )
    return signal_id

def test_queries_can_get_signals(session):
    # Setup test data
    empresa_id = insert_empresa(session)
    controlador_id = insert_controlador(session, empresa_id)
    signal_id = insert_signal(session, controlador_id)
    
    # Test queries
    queries = SignalQueries(session)
    signals = queries.get_signals_in_timeframe(
        controlador_id=controlador_id,
        start_time=datetime(2024, 1, 1),
        end_time=datetime(2024, 1, 2),
        user_permissions=['view_signals']
    )
    
    assert len(signals) == 1
    assert signals[0].values == {"temp": 25.5}
    assert signals[0].metadata == {"source": "sensor1"}

def test_queries_respect_permissions(session):
    # Setup test data
    empresa_id = insert_empresa(session)
    controlador_id = insert_controlador(session, empresa_id)
    signal_id = insert_signal(session, controlador_id)
    
    # Test queries without permissions
    queries = SignalQueries(session)
    signals = queries.get_signals_in_timeframe(
        controlador_id=controlador_id,
        start_time=datetime(2024, 1, 1),
        end_time=datetime(2024, 1, 2),
        user_permissions=[]  # No permissions
    )
    
    assert len(signals) == 0

def test_controlador_summary(session):
    # Setup test data
    empresa_id = insert_empresa(session)
    controlador_id = insert_controlador(session, empresa_id)
    signal_id = insert_signal(session, controlador_id)
    
    queries = SignalQueries(session)
    summaries = queries.get_controlador_summary(
        empresa_id=empresa_id,
        user_permissions=['view_dashboard']
    )
    
    assert len(summaries) == 1
    assert summaries[0].controlador_name == "Test Controller"
    assert summaries[0].signal_count == 1
    assert summaries[0].latest_values == {"temp": 25.5}

def test_repository_can_retrieve_empresa(session):
    # Setup
    empresa_id = insert_empresa(session)
    
    # Exercises
    repo = EmpresaRepository(session)
    retrieved = repo.get(empresa_id)
    
    # Verify
    assert retrieved.name == "Test Empresa"
    assert retrieved.phone_number == "1234567890"
    assert retrieved.email == "test@example.com"

def test_repository_can_list_empresas(session):
    # Setup
    empresa_id1 = insert_empresa(session)
    session.execute(
        text("INSERT INTO empresas (name, phone_number, email) VALUES (:name, :phone, :email)"),
        {
            "name": "Another Empresa",
            "phone": "9876543210",
            "email": "another@example.com"
        }
    )
    
    # Exercise
    repo = EmpresaRepository(session)
    empresas = repo.list()
    
    # Verify
    assert len(empresas) == 2
    assert any(e.name == "Test Empresa" for e in empresas)
    assert any(e.name == "Another Empresa" for e in empresas)
