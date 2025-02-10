import pytest
import src.domain.model as m
from sqlalchemy import text, insert, select
from datetime import datetime
from sqlalchemy.types import Float


def test_mapper_can_load_empresa(session):
    expected = m.Empresa(name="Test Empresa", phone_number="1234567890", email="test@example.com")

    session.execute(text("INSERT INTO empresas (name, phone_number, email) VALUES" 
                         '(:name, :phone_number, :email)'), 
                         dict(name=expected.name, phone_number=expected.phone_number, email=expected.email))

    # Query the empresa table and load into ORM object
    empresa = session.query(m.Empresa).filter_by(name=expected.name).first()
    
    assert empresa.name == expected.name
    assert empresa.phone_number == expected.phone_number 
    assert empresa.email == expected.email


def test_mapper_can_save_empresa(session):
    empresa = m.Empresa(name="Test Empresa", phone_number="1234567890", email="test@example.com")

    session.add(empresa)
    session.commit()

    row = session.execute(
        text("SELECT name, phone_number, email FROM empresas WHERE name = 'Test Empresa'")
    ).fetchone()
    assert row[0] == empresa.name
    assert row[1] == empresa.phone_number
    assert row[2] == empresa.email


def test_mapper_can_load_user(session):
    empresa = m.Empresa(name="Test Empresa", phone_number="1234567890", email="test@example.com")
    session.add(empresa)
    session.commit()

    expected = m.User(
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        password="secret123",
        phone_number="9876543210"
    )
    
    session.execute(
        text("""INSERT INTO users (first_name, last_name, email, password, phone_number, empresa_id) 
             VALUES (:first_name, :last_name, :email, :password, :phone_number, :empresa_id)"""),
        dict(
            first_name=expected.first_name,
            last_name=expected.last_name,
            email=expected.email,
            password=expected.password,
            phone_number=expected.phone_number,
            empresa_id=empresa.id
        )
    )

    user = session.query(m.User).filter_by(email=expected.email).first()
    
    assert user.first_name == expected.first_name
    assert user.last_name == expected.last_name
    assert user.email == expected.email
    assert user.password == expected.password
    assert user.phone_number == expected.phone_number


def test_mapper_can_save_user(session):
    empresa = m.Empresa(name="Test Empresa", phone_number="1234567890", email="test@example.com")
    session.add(empresa)
    session.commit()

    user = m.User(
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        password="secret123",
        phone_number="9876543210"
    )
    user._empresa = empresa
    
    session.add(user)
    session.commit()

    row = session.execute(
        text("SELECT first_name, last_name, email, password, phone_number FROM users WHERE email = :email"),
        dict(email="john@example.com")
    ).fetchone()
    
    assert row[0] == user.first_name
    assert row[1] == user.last_name
    assert row[2] == user.email
    assert row[3] == user.password
    assert row[4] == user.phone_number


def test_mapper_can_load_controlador(session):
    empresa = m.Empresa(name="Test Empresa", phone_number="1234567890", email="test@example.com")
    session.add(empresa)
    session.commit()

    config_data = {
        "settings": {
            "mode": "active",
            "thresholds": [20, 30, 40],
            "nested": {
                "key": "value",
                "enabled": True
            }
        }
    }

    expected = m.Controlador(
        name="Test Controller",
        phone_number="5555555555",
        config=config_data
    )
    
    stmt = insert(m.Controlador.__table__).values(
        name=expected.name,
        phone_number=expected.phone_number,
        config=config_data,  # JSONB will handle nested structures
        empresa_id=empresa.id
    )
    session.execute(stmt)
    session.commit()

    # Query using modern select()
    stmt = select(m.Controlador).where(
        # Can use JSONB operators in PostgreSQL
        m.Controlador.config['settings']['mode'].astext == 'active'
    )
    controlador = session.scalar(stmt)
    
    assert controlador.name == expected.name
    assert controlador.phone_number == expected.phone_number
    assert controlador.config == config_data
    # Test nested JSONB access
    assert controlador.config['settings']['nested']['enabled'] is True


def test_mapper_can_save_controlador(session):
    empresa = m.Empresa(name="Test Empresa", phone_number="1234567890", email="test@example.com")
    session.add(empresa)
    session.commit()

    controlador = m.Controlador(
        name="Test Controller",
        phone_number="5555555555",
        config={"setting1": "value1"}
    )
    controlador._empresa = empresa
    
    session.add(controlador)
    session.commit()

    row = session.execute(
        text("SELECT name, phone_number, config FROM controladores WHERE name = :name"),
        dict(name="Test Controller")
    ).fetchone()
    
    assert row[0] == controlador.name
    assert row[1] == controlador.phone_number
    assert row[2] == controlador.config


def test_mapper_can_load_signal(session):
    empresa = m.Empresa(name="Test Empresa", phone_number="1234567890", email="test@example.com")
    controlador = m.Controlador(name="Test Controller", phone_number="5555555555", config={})
    controlador._empresa = empresa
    session.add(empresa)
    session.add(controlador)
    session.commit()

    expected_tstamp = datetime.now()
    expected = m.Signal(
        tstamp=expected_tstamp,
        values={"temp": 25.5},
        latitude=40.7128,
        longitude=-74.0060,
        metadata={"source": "sensor1"},
        _controlador=controlador
    )
    
    # Use the ORM model's __table__ instead of raw SQL
    stmt = insert(m.Signal.__table__).values(
        tstamp=expected.tstamp,
        values=expected.values,
        latitude=expected.latitude,
        longitude=expected.longitude,
        metadata=expected.metadata,
        controlador_id=controlador.id
    )
    session.execute(stmt)
    session.commit()

    signal = session.query(m.Signal).filter_by(tstamp=expected_tstamp).first()
    
    assert signal.tstamp == expected.tstamp
    assert signal.values == expected.values
    assert signal.latitude == expected.latitude
    assert signal.longitude == expected.longitude
    assert signal.metadata == expected.metadata


def test_mapper_can_save_signal(session):
    empresa = m.Empresa(name="Test Empresa", phone_number="1234567890", email="test@example.com")
    controlador = m.Controlador(name="Test Controller", phone_number="5555555555", config={})
    controlador._empresa = empresa
    session.add(empresa)
    session.add(controlador)
    session.commit()

    tstamp = datetime.now()
    # Complex JSONB data for values and metadata
    values_data = {
        "sensors": {
            "temp": 25.5,
            "humidity": 60,
            "readings": [
                {"time": "10:00", "value": 24},
                {"time": "10:01", "value": 25}
            ]
        }
    }
    metadata_data = {
        "device": {
            "id": "sensor1",
            "firmware": "v1.2.3",
            "status": {
                "battery": 90,
                "connection": "stable"
            }
        }
    }

    signal = m.Signal(
        tstamp=tstamp,
        values=values_data,
        latitude=40.7128,
        longitude=-74.0060,
        metadata=metadata_data,
        _controlador=controlador
    )
    
    session.add(signal)
    session.commit()

    # Query using JSONB operators
    stmt = select(m.Signal).where(
        m.Signal.values['sensors']['temp'].cast(Float) > 20.0,
        m.Signal.metadata['device']['status']['connection'].astext == 'stable'
    )
    result = session.scalar(stmt)
    
    assert result.values == values_data
    assert result.metadata == metadata_data

